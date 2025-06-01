# MinIO-based Flask Upload & Session App

Bu layihə Flask + Terraform istifadə edərək MinIO-da session və fayl yükləmə sistemini qurur.

## Tətbiq:
- Session App (`5000` port)
- Upload App (`5001` port)
- MinIO + KMS + SSE inteqrasiyası (`9000` / `9001`)

## Başlatmaq:
```bash
terraform init
terraform apply

