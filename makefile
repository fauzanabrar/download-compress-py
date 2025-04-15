format:
	black streamlit-web/

web:
	streamlit run streamlit-web/src/app.py

backend:
	fastapi run backend.py

file:
	wget https://static.videezy.com/system/protected/files/000/012/427/statue.mp4 -O downloaded-files/statue.mp4