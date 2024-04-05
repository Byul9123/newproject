# newproject

1.프로젝트 소개 
  = 인스타그램을 기반으로 게시물과 댓글 좋아요기능을 포함한 게시판페이지 만들기 
  
***  
2.개발기간
  = 2024년 4월 3일 ~ 7일 
  
***
3.주요 기능
  =PYTHON, Flask, SQLite, HTML, CSS, JS
  
***
4.역할분담 및 팀원 구성
  = 이정호 : DB 추가(이미지,이미지 경로), 이미지 담당, 댓글 수정, 머지, 발표

  = 이한별 : DB (Book 모델, 댓글 수정 및 삭제), 댓글 생성 및 수정 및 삭제, 머지 ,발표 준비

  = 김동환 : 초기 DB 구성(POST 및 USER), 메인 화면 CSS  담당, 포스트 담당, 머지 , 로그인 및 회원가입

  = 임준성 : DB (좋아요 모델, 포스트 수정, 댓글 수정 및 삭제), 포스트 좋아요 담당, 좋아요 된 포스트 테이블 생성, 머지 
  
***
5. api
  =URL	                      API명
  /register		                GET, POST	
  /login		                  GET, POST
  /posts/create		            GET, POST
  /posts/delete/int:post_id		DELETE	
  /addBook		                POST	
  /book/edit/<int:book_id>		PATCH	
  /book/delete/<int:book_id>	DELETE	

  /addLike/int:post_id		    POST

***

![screenshot_2024-04-05_at_2 15 15___pm_720](https://github.com/Byul9123/newproject/assets/156772020/1c171a90-8172-44aa-8519-0d68f121ac78)

![screenshot_2024-04-05_at_2 15 51___pm_720](https://github.com/Byul9123/newproject/assets/156772020/71fe7b2e-30df-4905-8337-14cae3af60f7)

![screenshot_2024-04-05_at_2 16 00___pm_720](https://github.com/Byul9123/newproject/assets/156772020/461c7693-d589-4129-8848-2cf625c4606f)
