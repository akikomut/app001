import PySimpleGUI as sg
import wikipedia
from bs4 import BeautifulSoup
import requests
import unicodedata

# ------------------------------------------------------------------
# 入力チェック
def clean_string(str_tdate):
    # 前後空白を削除
    str_tdate = str_tdate.strip()
    # 全種類の空白を削除（改行文字も）
    str_tdate = str_tdate.rstrip()
    str_tdate = str_tdate.lstrip()
    str_tdate = unicodedata.normalize('NFKC', str_tdate)
    return str_tdate

# ------------------------------------------------------------------
# wikipediaデータ取得
def execute_get_wikidata(str_tdate):
    wikipedia.set_lang("ja")
    try:
        page = wikipedia.page(str_tdate)
    except wikipedia.exceptions.DisambiguationError:
        return None
    
    # ページ解析
    html = requests.get(page.url)
    soup = BeautifulSoup(html.content, "html.parser")

    res_url = page.url

    if soup.find(id="誕生日"):
        topic = soup.find(id="誕生日")
        ul_element = topic.find_next("ul")
        res_bd = ul_element.text
    else:
        res_bd = "データがありませんでした。"

    if soup.find(id="できごと"):
        topic = soup.find(id="できごと")
        ul_element = topic.find_next("ul")
        res_event = ul_element.text
    else:
        res_event = "データがありませんでした。"

    return (res_url, res_event, res_bd)

# ------------------------------------------------------------------
# 画面表示の値設定
font_name ="Meiryo UI"
label_title = "今日は何の日？"
label_memo = "■■ 調べたい日を入力してください。Wikipediaからデータ取得します。"
label1 = "日付："
value = "●月●日"
btn_get_data = "データ取得"

label_title2 = "■■ 取得結果"
label_memo2 = "取得したデータを確認のうえ適宜編集しましょう。"
label_title3 = "URL: "
label_event = "■この日のできごと"
label_bd = "■この日が誕生日の著名人"

# テーマ設定
sg.theme("Green")

# レイアウト設定
frame1 = sg.Frame("", 
    [
        [sg.Text(label_title, font=(font_name, 20), size=(30,1)),],
        [sg.Text(label_memo, font=(font_name, 12)),],
        [sg.Text(label1, font=(font_name, 12), size=(5,1)), 
        sg.InputText(value, font=(font_name, 12), size=(15,5), pad=(8,5), key="input_date"),
        sg.Button(btn_get_data, font=(font_name, 12), size=(15,5), pad=(5,5), bind_return_key=True)],
    ], size=(1010,120) # 幅、高さ
    )

frame2 = sg.Frame("",
    [
        [sg.Text(label_title2, font=(font_name, 12), size=(30,1)),],
        [sg.Text(label_title3, font=(font_name, 10), size=(5,1)),
        sg.InputText(font=(font_name, 10), size=(900,5), key="wikiurl")],
    ], size=(1010,100)
    )

frame3 = sg.Frame(label_event, 
    [
        [sg.Multiline(key="eve_output", size=(490,450)),],
    ], size=(500,500)
  )

frame4 = sg.Frame(label_bd, 
    [
        [sg.Multiline(key="bd_output", size=(490,450)),],
    ], size=(500,500)
  )

layout = [[frame1], [frame2], [frame3, frame4]]

# ウインドウ設定
window = sg.Window(label_title, layout, resizable=True)

# ------------------------------------------------------------------
# イベント処理
while True:
    try:
        # イベント待機
        event, values = window.read()
        # 終了するとき
        if event is None:
            break

        # データ取得ボタンを押したとき
        if event == btn_get_data:
            # 入力チェック
            str_tdate = values["input_date"]
            str_tdate = clean_string(str_tdate)
            
            # データ取得
            result = execute_get_wikidata(str_tdate)
            # 画面表示
            if result:
                res_url, res_event, res_bd = result
                window ["eve_output"].update(res_event)
                window ["bd_output"].update(res_bd)
                window ["wikiurl"].update(res_url)
                window ["input_date"].update(str_tdate)
                
            else:
                # 確認msg
                sg.popup_error("複数のページが見つかりました。確認してください。")

    except Exception as e:
        print("予期せぬ エラーが発生しました。")
        print(f'* 種類: {type(e)}')
        print(f'* 内容: {e}')

# 終了処理
window.close()

