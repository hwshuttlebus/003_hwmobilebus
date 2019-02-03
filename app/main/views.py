from flask import current_app, render_template, send_file, send_from_directory
from flask import make_response, request, url_for, redirect, flash
from flask_login import current_user, login_required
from datetime import datetime
from werkzeug.utils import secure_filename
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm
from ..decorators import admin_required, permission_required
from ..models import mUser, mRole, mPost, Event, mBus, mStation
from .. import db
from ..api_1_0.diagram import updateNumber
import flask_excel as excel
import os

@main.route('/', methods=['GET', 'POST'])
def index():
    if False == current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    return render_template('index.html')
    #return make_response(open('app/templates/index.html').read())

@main.route('/collectcardnum/')
@login_required
@admin_required
def updatecardnum():
    updateNumber()
    flash('更新乘客打卡信息!')
    return redirect(url_for('main.index'))

@main.route('/user/<mailaddr>')
def user(mailaddr):
    user = mUser.query.filter_by(mailaddr=mailaddr).first_or_404()
    #query for register bus name
    busrec1 = None
    busrec2 = None
    stations = user.stations.all()
    if stations is not None:
        if len(stations) >= 1:
            if stations[0] is not None:
                busrec1 = mBus.query.filter_by(id=stations[0].bus_id).first()
        if len(stations) >= 2:
            if stations[1] is not None:
                busrec2 = mBus.query.filter_by(id=stations[1].bus_id).first()
    return render_template('user.html', user=user, bus1=busrec1, bus2=busrec2)

@main.route('/userdel/<int:id>')
@login_required
@admin_required
def del_user(id):
    user = mUser.query.filter_by(id=id).first_or_404()
    try:
        db.session.delete(user)
        db.session.commit()
        flash('用户删除成功!')
    except:
        db.session.rollback()
    return redirect(url_for('main.index'))


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.campus = form.campus.data
        db.session.add(current_user)
        flash('您的资料已经更新！')
        return redirect(url_for('.user', mailaddr=current_user.mailaddr))
    form.name.data = current_user.name
    form.campus.data = current_user.campus
    return render_template('edit_profile.html', form=form)

@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = mUser.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.mailaddr = form.mailaddr.data
        user.confirmed = form.confirmed.data
        #user.role = mRole.query.get(form.role.data)
        user.role_id = form.role.data
        user.name = form.name.data
        user.campus = form.campus.data
        db.session.add(user)
        flash('资料已经更新！')
        return redirect(url_for('.user', mailaddr=user.mailaddr))
    form.mailaddr.data = user.mailaddr
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.campus.data = user.campus
    return render_template('edit_profile.html', form=form, user=user)

@main.route('/infoModal.html')
def infoModal():
    return render_template('server_partial/infoModal.html')

@main.route('/ngtemplates/showmaproute.html')
def showmap():
    return render_template('/ngtemplates/showmaproute.html')

#upload pdf
def allowed_file(filename, config):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in config


@main.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.static_folder, filename)

@main.route('/uploadposlb', methods=['GET', 'POST'])
def uploadposlb():
    #get query param
    campus = request.args.get('campus', 1, type=int)
    if campus == 1:
        campus = "libingroad"
    else:
        campus = "huankeroad"

    if request.method == 'POST':
        #check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        #if user does not select file, browser also
        #submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
            filename = secure_filename(file.filename)

            #judge filename
            if campus == "libingroad":
                if filename.rsplit('.', 1)[0] != 'layoutlb':
                    flash('file name is not layoutlb.pdf!')
                    return redirect(request.url)
            else:
                if filename.rsplit('.', 1)[0] != 'layouthk':
                    flash('file name is not layouthk.pdf!')
                    return redirect(request.url)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            flash('upload successfully!')
            return redirect(url_for('main.uploaded_file',filename=filename, campus=campus))
        else:
            flash('file format error!')
            return redirect(request.url)

    if campus == "huankeroad":
        return render_template('uploadpos.html', campus="环科路")
    else:
        return render_template('uploadpos.html', campus="李冰路")


@main.route('/export', methods=['GET'])
def exportbusstationinfo():
    #create a list of dictionary with key: busname, station, time
    record = []

    #handle for libingroad campus
    record.append(['李冰路园区'])
    allbus = mBus.query.filter_by(campus="libingroad").all()
    if allbus is not None:
        for bus in allbus:
            if bus.name is not None:
                #record bus line with one blank line
                record.append([''])
                record.append([bus.name])
                #record stations, currently only filter to company stations
                allstations = bus.stations.order_by(mStation.time).all()
                for station in allstations:
                    stationrec = []
                    if station.name is not None:
                        if True == station.dirtocompany:
                            stationrec.append(station.name)
                            stationrec.append(station.time.strftime('%H:%M'))
                            record.append(stationrec)

    record.append([''])
    record.append([''])
    record.append([''])
    record.append(['环科路园区'])
    allbus = mBus.query.filter_by(campus="huankeroad").all()
    if allbus is not None:
        for bus in allbus:
            if bus.name is not None:
                #record bus line with one blank line
                record.append([''])
                record.append([bus.name])
                #record stations, currently only filter to company stations
                allstations = bus.stations.order_by(mStation.time).all()
                for station in allstations:
                    stationrec = []
                    if station.name is not None:
                        if True == station.dirtocompany:
                            stationrec.append(station.name)
                            stationrec.append(station.time.strftime('%H:%M'))
                            record.append(stationrec)


    return excel.make_response_from_array(record, "xls", file_name="班车站点信息")



@main.route("/import", methods=['GET', 'POST'])
def doimport():
    #get query param
    campus = request.args.get('campus', 1, type=int)
    if campus == 1:
        campus = "libingroad"
    else:
        campus = "huankeroad"

    if request.method == 'POST':
        #first delete all bus and stations
        if (campus == "libingroad"):
            print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            stations = mStation.query.all()
            for item in stations:
                print('delete station:'+ str(item.name))
                db.session.delete(item)
                db.session.commit()
            buses = mBus.query.all()
            for item in buses:
                print('delete bus:'+ str(item.name))
                db.session.delete(item)
                db.session.commit()

        def mbus_init_func(row):
            #input check
            if row['名称'] == "" or row['名称'] is None \
                or row['编号']=="" or row['编号'] is None:
                return None

            b = mBus.query.filter_by(name=row['名称'], number=row['编号']).first()
            if b is not None:
                b.name = row['名称']
                b.number = row['编号']
                b.cz_name = row['车长']
                b.cz_phone = row['车长手机']
                b.sj_name = row['司机']
                b.sj_phone = row['司机手机']
                b.seat_num = row['座位数']
                b.campus = campus
            else:
                b = mBus(name=row['名称'], number=row['编号'], cz_name=row['车长'], cz_phone=row['车长手机'],
                        sj_name=row['司机'],sj_phone=row['司机手机'], seat_num=row['座位数'], campus=campus)

            return b

        def station_init_func(row):
            s = None
            #input check
            if row['站点'] == "" or row['站点'] is None or \
                row['计划发车时间']=="" or row['计划发车时间'] is None:
                return None

            print('station:'+row['站点'])
            if row['站点描述'] is not None:
                print('desc: '+row['站点描述'])

            timestr = str(row['计划发车时间'])
            datetimeobj = datetime.strptime(timestr.strip(), '%H:%M:%S').time()
            latlon = row['站点经纬度信息']
            lat = None
            lon = None
            direction = row['direction']
            if latlon is not "" and latlon is not None:
                lon = latlon.strip().split(',')[0]
                if lon is not None:
                    lon = float(lon)
                lat = latlon.strip().split(',')[1]
                if lat is not None:
                    lat = float(lat)
                #transfer from google coordinate to baidu
                from ..gpsutil import gcj02tobd09
                lon, lat = gcj02tobd09(lon, lat)
            else:
                lat = 0.0
                lon = 0.0

            b = mBus.query.filter_by(name=row['名称'], number=row['编号']).first()
            if b is not None:
                s = mStation.query.filter_by(name=row['站点'], bus_id=b.id, dirtocompany=direction).first()
                if s is not None:
                    s.name = row['站点']
                    s.description = row['站点描述']
                    s.time = datetimeobj
                    s.dirtocompany = True
                    s.lat = lat
                    s.lon = lon
                    s.campus = campus
                    s.bus_id = b.id
                    s.dirtocompany = direction
                else:
                    s = mStation(name=row['站点'], description=row['站点描述'], time=datetimeobj,
                                dirtocompany=direction, lat=lat, lon=lon, campus=campus, bus_id=b.id)

            return s

        request.save_book_to_database(
            field_name='file', session=db.session,
            tables=[mBus, mStation],
            initializers=[mbus_init_func, station_init_func])
        return redirect(url_for('.doimport'), code=302)
    return '''
    <!doctype html>
    <title>Upload an excel file</title>
    <h1>Excel file upload (xls, xlsx, ods please)</h1>
    <form action="" method=post enctype=multipart/form-data><p>
    <input type=file name=file><input type=submit value=Upload>
    </form>
    '''
