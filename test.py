import pandas as pd
import os

# 샘플 데이터 생성
soda = {'상품명': ['콜라', '사이다'], '가격': [2700, 2000]}
df = pd.DataFrame(soda)

# .to_csv 
# 최초 생성 이후 mode는 append
if not os.path.exists('output.csv'):
    df.to_csv('output.csv', index=False, mode='w', encoding='utf-8-sig')
else:
    df.to_csv('output.csv', index=False, mode='a', encoding='utf-8-sig', header=False)
