## api test

```python
# fast api 실행
python -m api.run
```

```bash
# api call 확인

# 인스턴스 외부
curl -X POST "${public_ip}:${fast_api_port}/predict" \
     -H "Content-Type: application/json" \
     -d '{
           "pclass": 1,
           "age": 30.0,
           "fare": 50.0,
           "sex": 1
         }'
         
# 인스턴스 내부
curl -X POST "${private_ip}:${fast_api_port}/predict" \
     -H "Content-Type: application/json" \
     -d '{
           "pclass": 1,
           "age": 30.0,
           "fare": 50.0,
           "sex": 1
         }'
```