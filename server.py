from bottle import default_app, request, route, static_file, template,run,error,redirect
from helps import is_trade_time
from stock_details import *
import datetime
import re



def check_stock_code(code,check_my_stock=False):
    if re.search(r'^(sh|sz)?\d{6}$', code):
        try:
            data = get_stock_detail([code])[0]

            if check_my_stock:

                with open('.my_stock', 'rb') as f:
                    stock_list = pickle.load(f)
                if code in stock_list:

                    return {"msg":"该股票已存在自选股中 无法再添加！" }

            return {"msg": "success", "data": data}

        except:
            return {"msg":"该股票代码:%s不存在！" % code}

    else:
        return {"msg":"请输入6位股票代码！"}


@route("/")
@route("/index")
def index():
    now_time = datetime.datetime.now()
    current_date = now_time.strftime('%Y-%m-%d')
    current_time = now_time.strftime('%H:%M:%S')
    trade_flag = is_trade_time(now_time)
    hs300_data = get_stock_detail(get_hs300())
    my_stock_data = get_stock_detail(get_my_stock())
    market_index_data = get_market_index()

    return template('index',current_date = current_date,
                            current_time = current_time,
                            my_stock_data = my_stock_data,
                            hs300_data = hs300_data,
                            market_index_data=market_index_data,
                            top_banner_data = get_top_banner(),
                            footer_string = random.choice(FOOTER_STRING),
                            trade_flag = trade_flag
                    )


@route('/index', method = 'post')
def index():

    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    current_time = datetime.datetime.now().strftime('%H:%M:%S')
    new_code = request.POST.get('add_code')
    delete_code = request.POST.get('delete_code')
    if new_code:
        code_msg = check_stock_code(new_code,check_my_stock=True) #检查股票有效性
        if code_msg['msg'] == "success":

            add_my_stock(new_code)

        return code_msg['msg']
    if delete_code:
        delete_my_stock(delete_code)


@route("/stock/<code>")
def stock_figure(code):
    current_time = datetime.datetime.now().strftime('%H:%M:%S')

    code_msg = check_stock_code(code) # 检查股票的有效性
    if code_msg['msg'] == "success":
        single_stock_detail = code_msg['data']
        history_data = get_stock_history(code)
        minute_data = get_stock_minute(code)
        return template('detail', history_data=history_data,
                        minute_data={"data": minute_data,
                                     "yestclose": single_stock_detail[6]},
                        stock_info=single_stock_detail,
                        current_time =current_time,
                        footer_string=random.choice(FOOTER_STRING)).replace('&#039;', "'")

    else:
        return template('error',
                        current_time=current_time,
                        footer_string=random.choice(FOOTER_STRING),
                        msg=code_msg['msg']
                        )


@route('/static/js/<filename>')
def server_static(filename):
    return static_file(filename, root='./static/js')

@route('/static/imgs/<filename>')
def server_static(filename):
    return static_file(filename, root='./static/imgs')

@route('/static/css/<filename>')
def server_static(filename):
    return static_file(filename, root='./static/css')


@error(404)
def error_404(error):
    current_time = datetime.datetime.now().strftime('%H:%M:%S')

    return template('error',current_time = current_time,
                            footer_string=random.choice(FOOTER_STRING),
                            msg = ''
                            )


@error(500)
def error_500(error):
    current_time = datetime.datetime.now().strftime('%H:%M:%S')

    return template('error',current_time = current_time,
                            footer_string=random.choice(FOOTER_STRING),
                            msg = '内部服务异常！你好像被庄家发现了！'
                            )

run(host = 'localhost', port = 8002, debug = True, reloader = True)
# application = default_app()


