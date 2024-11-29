document.addEventListener("DOMContentLoaded", function() {
    // The data variables are already defined in index.html
    
    // 生成年份的標籤
    const allYears = [...new Set([...Object.keys(releaseYearNetflix), ...Object.keys(releaseYearDisney)])].sort((a, b) => a - b);
    const ratings = Object.keys({...NetflixRating, ...DisneyRating});

    // 填充缺失數據
    const netflixData = ratings.map(rating => NetflixRating[rating] || 0);
    const disneyData = ratings.map(rating => DisneyRating[rating] || 0);
    const releaseYearCountsNetflix = allYears.map(year => releaseYearNetflix[year] || 0);
    const releaseYearCountsDisney = allYears.map(year => releaseYearDisney[year] || 0);

    // 評級分布圖表
    const RatingCtx = document.getElementById('ratingChart').getContext('2d');
    new Chart(RatingCtx, {
        type: 'bar',
        data: {
            labels: ratings,
            datasets: [
                {
                    label: 'Netflix',
                    data: netflixData,
                    backgroundColor: 'rgba(255, 99, 132, 0.5)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                },
                {
                    label: 'DisneyPlus',
                    data: disneyData,
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Rating'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Movies'
                    }
                }
            }
        }
    });

    // 發布年份趨勢圖表
    const releaseYearCtx = document.getElementById('releaseYearChart').getContext('2d');
    new Chart(releaseYearCtx, {
        type: 'line',
        data: {
            labels: allYears,
            datasets: [
                {
                    label: 'Netflix 發布年份趨勢',
                    data: releaseYearCountsNetflix,
                    borderColor: 'red',
                    fill: false,
                },
                {
                    label: 'Disney 發布年份趨勢',
                    data: releaseYearCountsDisney,
                    borderColor: 'blue',
                    fill: false,
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: '年份'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '發布影片數量'
                    }
                }
            }
        }
    });
});