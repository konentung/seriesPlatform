import pandas as pd
from flask import Flask, render_template, request
import os

# 讀取兩個 CSV 檔案
disney_df = pd.read_csv('./data/disney_plus_titles.csv')
netflix_df = pd.read_csv('./data/netflix_titles.csv')

# 合併兩個資料框
netflix_df['Platform'] = 'Netflix'
disney_df['Platform'] = 'DisneyPlus'
df = pd.concat([disney_df, netflix_df], ignore_index=True)

# 處理空值，避免後續篩選出現問題
df['listed_in'] = df['listed_in'].fillna('')
df['Platform'] = df['Platform'].fillna('')
df['title'] = df['title'].fillna('')
df['description'] = df['description'].fillna('')

# 定義函數來查詢包含特定類別的影片
def search_by_category(df, categories, include_all=False):
    """
    查詢包含指定類別的影片。
    
    參數：
    df (DataFrame): 合併後的影片資料。
    categories (list of str): 要查詢的類別列表。
    include_all (bool): 若為 True，則返回包含所有指定類別的影片；否則返回包含至少一個指定類別的影片。
    
    回傳：
    DataFrame: 符合查詢條件的影片資料。
    """
    # 建立查詢條件
    if include_all:
        condition = df['listed_in'].apply(lambda x: all(category in x for category in categories))
    else:
        condition = df['listed_in'].apply(lambda x: any(category in x for category in categories))
    
    return df[condition].drop_duplicates(subset=['title'])

# Flask 應用程序
app = Flask(__name__)

@app.route('/')
def index():
    # 生成圖表所需的數據
    release_year_netflix = df[df['Platform'] == 'Netflix']['release_year'].value_counts().sort_index().to_dict()
    release_year_disney = df[df['Platform'] == 'DisneyPlus']['release_year'].value_counts().sort_index().to_dict()
    netflix_rating = df[df['Platform'] == 'Netflix']['rating'].value_counts().to_dict()
    disney_rating = df[df['Platform'] == 'DisneyPlus']['rating'].value_counts().to_dict()

    return render_template(
        'index.html', 
        release_year_netflix=release_year_netflix,
        release_year_disney=release_year_disney,
        netflix_rating=netflix_rating,
        disney_rating=disney_rating,
    )

@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    if request.method == 'POST':
        # 從表單獲取用戶的偏好資料
        genres = request.form.getlist('genres')  # 改為多選類別
        platform = request.form.get('platform')
        page = int(request.form.get('page', 1))
        
        # 根據用戶偏好篩選結果
        filtered_df = df
        if genres:
            filtered_df = search_by_category(filtered_df, genres, include_all=False)
        if platform and platform.lower() != 'all':
            filtered_df = filtered_df[filtered_df['Platform'].str.lower() == platform.lower()]

        # 設置分頁，每頁顯示5個結果
        results_per_page = 10
        start_idx = (page - 1) * results_per_page
        end_idx = start_idx + results_per_page
        paginated_df = filtered_df.iloc[start_idx:end_idx]

        # 檢查是否有推薦結果
        if filtered_df.empty:
            recommendations = [{'title': '無結果', 'Platform': '', 'description': '找不到符合您偏好的內容，請嘗試其他選項。'}]
        else:
            # 將分頁結果轉換為列表
            recommendations = paginated_df[['title', 'Platform', 'description']].to_dict(orient='records')

        return render_template('recommend.html', recommendations=recommendations, page=page, total_pages=(len(filtered_df) + results_per_page - 1) // results_per_page)

    # 如果是 GET 方法，則只顯示空的推薦頁面或重定向至首頁
    return render_template('recommend.html', recommendations=[], page=1, total_pages=1)

if __name__ == '__main__':
    app.run()