from PyInstaller.__main__ import run
# -F:打包成一个EXE文件
# -w:不带console输出控制台，window窗体格式
# --paths：依赖包路径
# --icon：图标
# --noupx：不用upx压缩
# --clean：清理掉临时文件

#资源打包 需要加 basedir
# if getattr(sys, 'frozen', False):
#     basedir = sys._MEIPASS
# else:
#     basedir = os.path.dirname(__file__)
#filepath = basedir + relative_path
##all data collected into one folder (include database)
#but if pack to one file, dataset should put into other folder

#多进程需要加入 mul_process_package.py
#主文件 加入multiprocessing.freeze_support() 和 import mul_process_package

if __name__ == '__main__':
    opts = ['-y','-F','-w','-i','sample\\logo-title.ico',#'--add-data', 'sample;sample', '--add-data', 'images;images',
            '--hidden-import','PyQt5.sip',
            '--clean',
            'run.py']

    run(opts)