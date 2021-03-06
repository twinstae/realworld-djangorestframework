# realworld-djangorestframework

DjangoRestFramework로 realword spec RestApi 구현
## 1. Crud와 relation 구현
- Article
  - author -> JwtUser, N:1 Foreign Key
  - tags -> Tag, N:N, ManyToManyField
- Comment
  - article, author -> Article, JwtUser, N:1, Foreign Key
- Tag
  - Article에 속한 N:N, ManyToMany 관계
- Follow
  - follows -> Profile to Profile self, N:N, ManyToMany
- Favorite 
  - favorites -> Article N:N, ManyToMany

## 2. JWT 을 이용한 인증. 회원가입, 로그인, 정보 변경 구현.
- custom JwtUser AuthUser클래스와 jwt 백엔드
- bio와 image를 포함한 Profile 확장

## 3. 요청 응답 구조
urls
-> view -> context validation
  -> serializer -> validation, create, update, pagination, filter
    -> models ORM
  -> response, status
  -> renderer
  
[원본 레포지토리](https://github.com/gothinkster/django-realworld-example-app)에 추가한 부분

## 4. url, view, client test
- 공통 부분 testing_utils로 추상화
- 특이 케이스 validation 포함
- test coverage 96%
- model, serializer, renderer테스트 미포함...

## 5. 과도한? 리팩토링 OOP Overkill
- validation, filter, get context 메소드, 함수 추출, 책임 분리
- follow/unfollow, favorite/unfavorite 람다를 이용한 strategy 패턴으로 추상화

## 6. object level permission
- 아마 원본 제작자가 까먹은 것 같은데 몇가지 구현이 안된 부분들을 구현했다.
- Article destroy
- update, destroy only by author. 원본에서는 인증 받은 유저라면 Article과 Comment를 수정하고 삭제할 수 있다. (자기가 쓴 게 아니라도!)
