CUDA_VISIBLE_DEVICES=2 python src/main.py --config=ow_qmix --env-config=sc2 with env_args.map_name=3s5z w=0.5 epsilon_anneal_time=50000 t_max=2005000
sleep 3

CUDA_VISIBLE_DEVICES=2 python src/main.py --config=ow_qmix --env-config=sc2 with env_args.map_name=3m w=0.5 epsilon_anneal_time=50000 t_max=1005000 
sleep 3

CUDA_VISIBLE_DEVICES=2 python src/main.py --config=ow_qmix --env-config=sc2 with env_args.map_name=1c3s5z w=0.5 epsilon_anneal_time=50000 t_max=2005000
sleep 3

CUDA_VISIBLE_DEVICES=2 python src/main.py --config=ow_qmix --env-config=sc2 with env_args.map_name=8m w=0.5 epsilon_anneal_time=50000 t_max=2005000

