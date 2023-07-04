import transformers
from typing import Optional, Dict, Sequence
from dataclasses import dataclass, field
import torch
from torch.nn.utils.rnn import pad_sequence
from datasets import load_dataset, Dataset
import copy
from arguments import DataArguments

@dataclass
class DataCollatorForCausalLM(object):
    tokenizer: transformers.PreTrainedTokenizer

    def __call__(self, instances: Sequence[Dict]) -> Dict[str, torch.Tensor]:
        input_ids, labels = tuple([torch.LongTensor(instance[key][0]) for instance in instances] for key in ("input_ids", "labels"))
        input_ids = torch.nn.utils.rnn.pad_sequence(
            input_ids, batch_first=True, padding_value=self.tokenizer.pad_token_id
        )
        labels = torch.nn.utils.rnn.pad_sequence(labels, batch_first=True, padding_value=-100)
        return dict(
            input_ids=input_ids,
            labels=labels,
            attention_mask=input_ids.ne(self.tokenizer.pad_token_id),
        )

def make_data_module(tokenizer: transformers.PreTrainedTokenizer, args: DataArguments) -> Dict:
    
    def format_data(example):
        
        tokenized_sources = tokenizer(example['input'], return_attention_mask=False)['input_ids']   # add <s> in front
        tokenized_targets = tokenizer(example['output'], return_attention_mask=False, add_special_tokens=False)['input_ids']
        
        all_input_ids = []
        all_labels = []
        s = tokenized_sources
        # args.dataset_max_length = 2048
        t = tokenized_targets[:args.dataset_max_length - len(s) - 1] + [tokenizer.pad_token_id]
        
        input_ids = torch.LongTensor(s+t)
        if tokenizer.pad_token_id is None:
            raise Exception("This tokenizer has no pad_token_id")
        
        labels = torch.LongTensor([tokenizer.pad_token_id] * len(s) + t)
        
        assert len(input_ids) == len(labels)
        
        all_input_ids.append(input_ids)
        all_labels.append(labels)
        return dict(input_ids=all_input_ids, labels=all_labels)
    
    dataset = Dataset.from_json(args.dataset_path)
    print(dataset[0])
    dataset = dataset.map(format_data)
    dataset = dataset.remove_columns(
            [col for col in dataset.column_names if col not in ['input_ids', 'labels']]
    )
    print(dataset[0])
    
    dataset = dataset.train_test_split(test_size=args.test_split_size)

    data_collator = DataCollatorForCausalLM(
        tokenizer=tokenizer, 
    )
    
    return dict(
        train_dataset=dataset['train'],
        eval_dataset=dataset['test'],
        data_collator=data_collator
    )
