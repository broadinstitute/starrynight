default:
  @just --list

dev: dev_conductor dev_cron dev_canvas

dev_conductor:
  pueue add 'fastapi dev --host 0.0.0.0 ./conductor/src/conductor/main.py'

dev_cron:
  pueue add 'python ./conductor/src/conductor/cron.py'

[working-directory: 'canvas']
dev_canvas:
  pueue add 'npm run dev'
