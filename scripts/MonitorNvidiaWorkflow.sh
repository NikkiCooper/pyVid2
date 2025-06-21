#!/bin/bash

# Perfect monitoring setup for your photography app
#watch -n 0.5 'nvidia-smi --query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw --format=csv,noheader,nounits | awk -F, "{printf \"GPU: %s%% | VRAM: %s/%s MB | Temp: %s°C | Power: %s W\n\", \$2, \$3, \$4, \$5, \$6}"'
watch -n 0.5 'nvidia-smi --query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw --format=csv,noheader,nounits | awk -F, "{temp_f = (\$5 * 9/5) + 32; printf \"GPU: %s%% | VRAM: %s/%s MB | Temp: %.0f°F | Power: %s W\n\", \$2, \$3, \$4, temp_f, \$6}"'