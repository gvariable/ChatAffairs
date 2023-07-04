import copy
import os
import sys
import torch
from os.path import join
from transformers import HfArgumentParser
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig, Trainer
from transformers import set_seed
import transformers
import logging
from dataset import make_data_module
from dataclasses import asdict
from arguments import *
from transformers.deepspeed import HfDeepSpeedConfig
from transformers.trainer_utils import PREFIX_CHECKPOINT_DIR
from peft import (
    LoraConfig,
    get_peft_model,
    PeftModel,
)
import wandb
import time
python_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
print("PYTHON_PATH", python_path)
sys.path.append(python_path)

logging_file_path = f"./lora_logs.log"

handlers = [
    logging.FileHandler(logging_file_path),
    logging.StreamHandler(sys.stdout)
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=handlers
)

logger = logging.getLogger(__name__)

class SavePeftModelCallback(transformers.TrainerCallback):
    def save_model(self, args, state, kwargs):
        logger.info('Saving PEFT checkpoint...')
        if state.best_model_checkpoint is not None:
            checkpoint_folder = os.path.join(state.best_model_checkpoint, "adapter_model")
        else:
            checkpoint_folder = os.path.join(args.output_dir, f"{PREFIX_CHECKPOINT_DIR}-{state.global_step}")

        peft_model_path = os.path.join(checkpoint_folder, "adapter_model")
        kwargs["model"].save_pretrained(peft_model_path)

    def on_save(self, args, state, control, **kwargs):
        self.save_model(args, state, kwargs)
        return control

    def on_train_end(self, args, state, control, **kwargs):
        def touch(fname, times=None):
            with open(fname, 'a'):
                os.utime(fname, times)

        touch(join(args.output_dir, 'completed'))
        self.save_model(args, state, kwargs)

def train():
    parser = HfArgumentParser((ModelArguments, DataArguments, MyTrainingArguments))
    if sys.argv[-1].endswith(".yaml"):
        model_args, data_args, training_args = parser.parse_yaml_file(yaml_file=os.path.abspath(sys.argv[-1]))
    else:
        model_args, data_args, training_args = parser.parse_args_into_dataclasses()
    
    logger.info(training_args) 

    set_seed(training_args.seed)

    if training_args.local_rank in [-1, 0]:
        wandb_config = copy.deepcopy(asdict(training_args))
        wandb_config.update(asdict(model_args))
        wandb_config.update(asdict(data_args))
        wandb.init(
            project="ChatLaw",
            name=time.strftime("%Y-%m-%d-%H-%M-%S"),
            config=wandb_config
        )
    
    logger.info(f"start loading tokenizer.")
    tokenizer = AutoTokenizer.from_pretrained(
        model_args.model_name_or_path,
        use_fast=False,
        padding_side='right'
    )
    for token, token_id in ((tokenizer.pad_token, tokenizer.pad_token_id), 
                            (tokenizer.eos_token, tokenizer.eos_token_id), 
                            (tokenizer.bos_token, tokenizer.bos_token_id),
                            (tokenizer.unk_token, tokenizer.unk_token_id)):
        logging.info("{token} {token_id}".format(token=str(token), token_id=str(token_id)))
        
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.unk_token
        tokenizer.pad_token_id = tokenizer.unk_token_id
        logging.info("set pad_token to {unk_token}".format(unk_token=tokenizer.pad_token))
        
    data_module = make_data_module(tokenizer, data_args)
    
    if training_args.deepspeed is not None:
        ds_config = training_args.deepspeed
        dschf = HfDeepSpeedConfig(ds_config)
        
    config = AutoConfig.from_pretrained(model_args.model_name_or_path)
    config.gradient_checkpointing = training_args.gradient_checkpointing
    logger.info(f"start loading model.")
    
    no_deepspeed_params = {
        "device_map": "auto",
        "torch_dtype": torch.float32,
    }
    if training_args.deepspeed is not None:
        no_deepspeed_params = {}
    model = AutoModelForCausalLM.from_pretrained(
        model_args.model_name_or_path,
        config=config,
        **no_deepspeed_params,
    )
    
    if model_args.lora_path is not None:
        model = PeftModel.from_pretrained(model, model_args.lora_path, is_trainable=True)
    else:
        target_modules = training_args.trainable.split(',')
        lora_rank = training_args.lora_rank
        lora_dropout = training_args.lora_dropout
        lora_alpha = training_args.lora_alpha
        logger.info(f"target_modules: {target_modules}")
        logger.info(f"lora_rank: {lora_rank}")
        peft_config = LoraConfig(
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=target_modules,
            r=lora_rank, lora_alpha=lora_alpha, 
            lora_dropout=lora_dropout)
        model = get_peft_model(model, peft_config)
    model.enable_input_require_grads()
    
    setattr(model, 'model_parallel', True)
    setattr(model, 'is_parallelizable', True)
    model.config.use_cache = False
    
    trainer = Trainer(
        model=model,
        args=training_args,
        tokenizer=tokenizer,
        compute_metrics=None,
        **data_module,
    )
    trainer.add_callback(SavePeftModelCallback)
    
    if training_args.do_train:
        trainer.train()
        
if __name__ == "__main__":
    train()
