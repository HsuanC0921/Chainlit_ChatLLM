MODEL=models/breezedolphin-slerp-0.1.Q4_K_M.gguf
python -m llama_cpp.server --model $MODEL --n_ctx 16192
