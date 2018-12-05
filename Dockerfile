FROM alpine:latest

VOLUME			/devlog
ADD		.	/devlog
WORKDIR			/devlog

RUN adduser -D kyle &&				\
	apk update && 				\
	apk add make python3 &&			\
	pip3 install -r requirements.txt

USER		kyle

ENTRYPOINT [ "make" ]
CMD [ "devserver" ]
