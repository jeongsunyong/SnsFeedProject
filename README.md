# SnsFeedProject

------------------------------------------------------------------------------------
## 시연
1.링크 ) http://snsFeed.http://snsfeed.chickenkiller.com:8081/
2. 상단 sns 아이콘 : sns로그인
3. sns최초 로그인 시 메일 계정 입력(ID/PW)
4. 다른 sns 로그인 시 같은 계정 입력하면 연동.
5. 로그인 후 메인 화면에서 검색 및 데이터 가져오기 가능.

## 실행 방법
(1) Frontend
- node.js 설치
  - 14.x LTS 버전 설치 : https://nodejs.org/ko/download/
  - 아래 명령으로 정상 설치 확인한다. 
    ```sh
    node -v
    npm -v
    ```
  - 명령이 동작하지 않을 경우 환경변수 설정 확인.
- 패키지 설치
  - npm i
- 실행
  - npm run serve

(2) Backend
```sh
git clone https://github.com/jeongsunyong/adminBackend.git

python manage.py makemigrations  
python manage.py migrate  
python manage.py runserver

```
