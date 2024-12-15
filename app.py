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

# 處理空值
df['listed_in'] = df['listed_in'].fillna('')
df['Platform'] = df['Platform'].fillna('')
df['title'] = df['title'].fillna('')
df['description'] = df['description'].fillna('')

all_genres = sorted(set(genre.strip() for genres in df['listed_in'] for genre in genres.split(',')))

# 定義查詢函數
def search_by_category(df, categories, include_all=False):
    if include_all:
        condition = df['listed_in'].apply(lambda x: all(category in x for category in categories))
    else:
        condition = df['listed_in'].apply(lambda x: any(category in x for category in categories))
    return df[condition].drop_duplicates(subset=['title'])

# Flask 應用程序
app = Flask(__name__)

@app.route('/')
def index():
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
        genres = request.form.get('genres', '')
        if genres and not isinstance(genres, list):
            genres = genres.split(',')
        elif not genres:
            genres = []

        platform = request.form.get('platform', 'All')
        page = int(request.form.get('page', 1))

        filtered_df = df
        if genres:
            filtered_df = search_by_category(filtered_df, genres, include_all=False)
        if platform.lower() != 'all':
            filtered_df = filtered_df[filtered_df['Platform'].str.lower() == platform.lower()]

        results_per_page = 10
        start_idx = max((page - 1) * results_per_page, 0)
        end_idx = min(start_idx + results_per_page, len(filtered_df))

        if not filtered_df.empty:
            paginated_df = filtered_df.iloc[start_idx:end_idx]
            recommendations = paginated_df[['title', 'Platform', 'description']].to_dict(orient='records')
        else:
            recommendations = [{'title': '無結果', 'Platform': '', 'description': '找不到符合您偏好的內容，請嘗試其他選項。'}]

        total_pages = (len(filtered_df) + results_per_page - 1) // results_per_page
        return render_template(
            'recommend.html',
            recommendations=recommendations,
            genres=genres,
            platform=platform,
            page=page,
            total_pages=total_pages,
            all_genres=all_genres
        )

    return render_template('recommend.html', recommendations=[], genres=[], platform='All', page=1, total_pages=1, all_genres=all_genres)

if __name__ == '__main__':
    app.run()
