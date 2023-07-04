export NCCL_P2P_DISABLE=1
set -x
port=$(shuf -i25000-30000 -n1)
deepspeed --master_port "$port" --include localhost:0,1,2,3,4,5,6,7 src/train.py config/args.yaml