from dataclasses import dataclass, field
from typing import Optional
from transformers import TrainingArguments


@dataclass
class ModelArguments:
    model_name_or_path: Optional[str] = field(default="llama-7B")
    cache_dir: Optional[str] = field(default='../llama/checkpoint')
    lora_path: Optional[str] = field(default=None)

@dataclass
class DataArguments:
    dataset_path: str = field(default='path')
    test_split_size: float = field(default=0.0001)
    dataset_max_length: int = field(default=1024)
    
@dataclass
class MyTrainingArguments(TrainingArguments):
    trainable : Optional[str] = field(default="q_proj,v_proj")
    lora_rank : Optional[int] = field(default=8)
    lora_dropout : Optional[float] = field(default=0.1)
    lora_alpha : Optional[float] = field(default=32.)
    modules_to_save : Optional[str] = field(default=None)
    debug_mode : Optional[bool] = field(default=False)
    peft_path : Optional[str] = field(default=None)
    