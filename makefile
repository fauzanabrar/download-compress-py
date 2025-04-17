install:
	pip install -r streamlit-web/requirements.txt
	
	if [ "$(shell uname -s)" = "Linux" ]; then \
		if [ -f /etc/os-release ] && grep -q "Ubuntu" /etc/os-release; then \
			sudo apt update && sudo apt upgrade -y; \
			sudo apt install -y ffmpeg; \
		fi \
	fi
	
	npm i -g pm2

format:
	black streamlit-web/

web:
	streamlit run streamlit-web/src/app.py --server.port 8501

backend:
	fastapi run backend.py --port 8000

web-end:
	pm2 start "make web" --name web 
	pm2 start "make backend" --name backend

restart:
	pm2 restart all

restart-web:
	pm2 restart web

file:
	wget https://static.videezy.com/system/protected/files/000/012/427/statue.mp4 -O downloaded-files/statue.mp4