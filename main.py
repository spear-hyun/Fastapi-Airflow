from fastapi import FastAPI
from fastapi.responses import FileResponse
import pandas as pd
from datetime import datetime, date
import time
app = FastAPI()

@app.get("/")
def total_chart():
    music_chart = pd.read_csv("./music_chart.csv")
    
    
    
    # HTML 테이블 생성
    html_table = "<head>\n<link rel='stylesheet' type='text/css' href='./styles.css'>\n</head>\n"
    html_table += "<title>Total_chart</title>\n"
    html_table += f"<h1>{str(date.today()).split('-')[0]}년 {str(date.today()).split('-')[1]}월 {str(date.today()).split('-')[2]}일 {(str(datetime.now()).split()[1])[:2]}시 음악차트</h1>\n"
    html_table += "<table>\n"
    html_table += "<tr>\n"
    html_table += "<th>Rank</th>\n"
    html_table += "<th>Image</th>\n"
    html_table += "<th>Title</th>\n"
    html_table += "<th>Artist</th>\n"
    html_table += "<th>Rank Score</th>\n"
    html_table += "</tr>\n"

    for index, row in music_chart.iterrows():
        html_table += "<tr>\n"
        html_table += f"<td>{row['Rank']}</td>\n"
        html_table += f"<td><img src='{row['Img_src']}' alt='Album Image' width='140' height='140'></td>\n"
        html_table += f"<td>{row['Title']}</td>\n"
        html_table += f"<td>{row['Artist']}</td>\n"
        html_table += f"<td>{row['Rank_score']}</td>\n"
        html_table += "</tr>\n"

    html_table += "</table>"

    # HTML 파일 생성
    with open('music_chart.html', 'w') as file:
        file.write(html_table)

    
    return FileResponse('./music_chart.html')


    if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
        
        
        
        

@app.get("/melon")
def ba():
    return "바보"