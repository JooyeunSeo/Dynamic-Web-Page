import plotly.graph_objs as go
import plotly.offline as pyo

def create_exchange_graph(dates, rates, title, past_date=None, recent_date=None):
    """
    Plotly 그래프 생성 및 HTML div 반환
    :param dates: 날짜 리스트 (YYYY-MM-DD 문자열)
    :param rates: 환율 값 리스트
    :param title: 그래프 제목
    :param past_date: 강조할 과거 날짜 (YYYY-MM-DD 문자열)
    :param recent_date: 강조할 현재 날짜 (YYYY-MM-DD 문자열)
    :return: Plotly div 문자열
    """

    # Scatter 그래프 생성: 날짜(x축)와 환율(y축)을 연결하는 선 그래프
    trace = go.Scatter(
        x=dates,
        y=rates,
        mode='lines',
        name=title,
        line=dict(color='#585858', width=1),
    )

    # Shape: start_date와 recent_date 구간 강조
    shapes = []
    if past_date and recent_date:
        shapes.append(dict(
            type='rect',
            xref='x', yref='paper',  # yref='paper' -> y축 전체(0~1)
            x0=past_date,
            x1=recent_date,
            y0=0,
            y1=1,
            fillcolor='rgba(255, 255, 30, 0.3)',
            line=dict(width=0),  # 테두리 없음
            layer='below'  # 선 그래프 아래에 표시
        ))

    # Layout: 그래프 제목, x축과 y축 라벨, 배경색
    layout = go.Layout(
        title=dict(
            text=title,
            x=0.5,              # 가운데 정렬
            xanchor='center',   # x 위치 기준
            font=dict(color='black', size=23)
        ),
        annotations=[dict(
            text=f"{dates[0]} - {dates[-1]}",
            x=0.5, y=1.11, xref='paper', yref='paper',
            showarrow=False, font=dict(size=14, color='gray'), xanchor='center'
        )],
        xaxis=dict(title='Date'),
        yaxis=dict(title='Rate'),
        plot_bgcolor='rgb(246,246,246)',
        shapes=shapes
    )

    # Figure 객체 생성: 데이터와 레이아웃을 합쳐 Plotly Figure 생성
    fig = go.Figure(data=[trace], layout=layout)

    # HTML div 문자열로 그래프 변환
    graph_div = pyo.plot(fig, output_type='div', include_plotlyjs=False)

    # output_type='div' => HTML div 반환, include_plotlyjs=False => 외부에서 Plotly JS 불러오기
    return graph_div