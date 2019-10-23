from flask import render_template, flash, redirect, url_for, request
from demo import app
from forms import LoginForm, RegistrationForm, AddPodcastForm, AddEpisodeForm, EditPodcastForm, EditEpisodeForm
from flask_login import login_required, current_user, login_user, logout_user
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from models import User, Podcast, Episode
from demo import db
import os
import shutil
import rss_lib
from datetime import datetime
from PIL import Image

##################################################################################
# can this be set automatically
path = "/home/a_user/demo/app"
web_path = "http://127.0.0.1:8000" # only local what is the remote address?
##################################################################################

##################################################################################
# ADD EPISODE
##################################################################################
@app.route('/add_eps/<username>/<pod_id>/', methods=['GET', 'POST'])
@login_required
def add_eps(username,pod_id):

    user = User.query.filter_by(username=username).first_or_404()
    podcast = Podcast.query.filter_by(id=pod_id).first_or_404()
    podcast.buildtime = datetime.utcnow()

    form = AddEpisodeForm()
    if form.validate_on_submit():

        epaudio = form.epaudio.data
        filename = secure_filename(epaudio.filename)

        if os.path.exists(os.path.join(path, 'static/'+str(user.id)+'/'+str(podcast.id))):
            epaudio.save(os.path.join(path, 'static/'+str(user.id)+'/'+str(podcast.id), filename))

        else:
            os.mkdir(os.path.join(path, 'static/'+str(user.id)+'/'+str(podcast.id)))
            epaudio.save(os.path.join(path, 'static/'+str(user.id)+'/'+str(podcast.id), filename))

        ###############################################################
        # need to also construct and insert link to rss feed
        ###############################################################
        ep = Episode(epname=form.epname.data, epnum=form.epnum.data, epdesc=form.epdesc.data, eplink=form.eplink.data, pod_id=pod_id, audio_path=filename, it_sum=form.it_sum.data, it_subtitle=form.it_subtitle.data)

        ######################################################################
        # Add RSS episode
        rss = rss_lib.rss_add_ep(podcast,ep)

        ######################################################################

        db.session.add(ep)
        db.session.commit()

        return redirect(url_for('podcast', pod_id=podcast.id, user_id=user.id))

    return render_template('add_eps.html', title='Add Episode', form=form)


##################################################################################
# ADD PODCAST
##################################################################################
@app.route('/user/<username>/add_pod', methods=['GET', 'POST'])
@login_required
def add_pod(username):

    user = User.query.filter_by(username=username).first_or_404()

    form = AddPodcastForm()
    if form.validate_on_submit():

        # save icon
        podicon = form.podicon.data
        filename = secure_filename(podicon.filename)

        podcast = Podcast(author=form.author.data, podname=form.podname.data, poddesc=form.poddesc.data, user_id=user.id, username=user.username, image_path=filename,
                it_own_name=form.it_own_name.data, it_own_email=form.it_own_email.data, it_cat=form.it_cat.data, it_subcat=form.it_subcat.data, 
                it_sum=form.it_sum.data, it_subtitle=form.it_subtitle.data, it_keys=form.it_keys.data, it_explicit=form.it_explicit.data)

        podcast.buildtime = datetime.utcnow()

        db.session.add(podcast)
        db.session.commit()

        if os.path.exists(os.path.join(path, 'static/'+str(user.id)+'/'+str(podcast.id))):
            #podicon.save(os.path.join(path, 'static/'+str(user.id)+'/'+str(podcast.id), filename))
            podicon.save(os.path.join(path, 'static/'+str(user.id)+'/'+str(podcast.id), filename))

        elif os.path.exists(os.path.join(path, 'static/'+str(user.id))):
            os.mkdir(os.path.join(path, 'static/'+str(user.id)+'/'+str(podcast.id)))
            #podicon.save(os.path.join(path, 'static/'+str(user.id)+'/'+str(podcast.id), filename))
            podicon.save(os.path.join(path, 'static/'+str(user.id)+'/'+str(podcast.id), filename))

        else:
            os.mkdir(os.path.join(path, 'static/'+str(user.id)))
            os.mkdir(os.path.join(path, 'static/'+str(user.id)+'/'+str(podcast.id)))
            #podicon.save(os.path.join(path, 'static/'+str(user.id)+'/'+str(podcast.id), filename))
            podicon.save(os.path.join(path, 'static/'+str(user.id)+'/'+str(podcast.id), filename))

        # attempt to resize image to be square
        im = Image.open(os.path.join(path, 'static/'+str(user.id)+'/'+str(podcast.id), filename))
        w,h = im.size
        rim = im.resize((min(w,h),min(w,h)))
        rim.save(os.path.join(path, 'static/'+str(user.id)+'/'+str(podcast.id), filename))

        ######################################################################a
        # Add podcast link
        podcast.podlink = web_path +"/"+str(user.id)+"/"+str(podcast.id)

        # Create RSS
        rss = rss_lib.rss_create(podcast)

        # Save RSS
        rss_path = rss_lib.rss_save(rss,user,podcast)
        #podcast = Podcast.query.filter_by(id=pod_id).first_or_404()

        podcast.rsslink = rss_path

        db.session.commit()         # commit updated rss link and podcast link
        ######################################################################

        #flash('Congratulations, you added a podcast!')
        # return redirect(url_for('index'))
        return redirect(url_for('profile', pod_id=podcast.id, username=user.username))

    return render_template('add_pod.html', title='Add Podcast', form=form)

##################################################################################
# DELETE EPISODE
##################################################################################
@app.route('/delete_ep/<username>/<pod_id>/<ep_id>')
@login_required
def delete_ep(username,pod_id,ep_id):

    # TODO: Also delete associated images, episodes, and audio files

    ep = Episode.query.filter_by(id=ep_id).first_or_404()
    user = User.query.filter_by(username=username).first_or_404()

    if ep != None:

        # Delete data on server
        os.remove("rat/app/static/" + str(user.id) + "/" + str(pod_id) + "/" + ep.audio_path)
        #try:
        #    os.remove("rat/app/static/" + str(podcast.user_id) + "/" + str(podcast.id) + "/" + ep.epaudio)
        #except:
        #    print("Deleting data on the server failed")

    # Delete data in Database
        db.session.delete(ep)
        db.session.commit()
        flash('Congratulations, you deleted a podcast episode!')
        #return redirect(url_for('index'))
        return redirect(url_for('podcast', pod_id=pod_id, user_id=user.id))

    else:
        flash('Podcast episode deletion failed!')
        #return redirect(url_for('index'))
        return redirect(url_for('podcast', pod_id=pod_id, user_id=user.id))

##################################################################################
# DELETE PODCAST
##################################################################################
@app.route('/user/<username>/delete_pod/<pod_id>')
@login_required
def delete_pod(username,pod_id):

    # TODO: Also delete associated images, episodes, and audio files

    podcast = Podcast.query.filter_by(id=pod_id).first_or_404()

    if podcast != None:

        # Delete data on server
        try:
            shutil.rmtree("rat/app/static/" + str(podcast.user_id) + "/" + str(podcast.id))
        except:
            print("Deleting data on the server failed")

        # Delete data in Database
        db.session.delete(podcast)
        db.session.commit()
        flash('Congratulations, you deleted a podcast!')
        #return redirect(url_for('index'))
        return redirect(url_for('profile', pod_id=podcast.id, username=username))

    else:
        flash('Podcast deletion failed!')
        #return redirect(url_for('index'))
        return redirect(url_for('profile', pod_id=podcast.id, username=username))

##################################################################################
# EDIT EPISODE
##################################################################################
@app.route('/edit_pod/<username>/<pod_id>/<ep_id>', methods=['GET', 'POST'])
@login_required
def edit_ep(username,pod_id,ep_id):

    user = User.query.filter_by(username=username).first_or_404()
    ep = Episode.query.filter_by(id=ep_id).first_or_404()

    form = EditEpisodeForm(obj=ep)
    if form.validate_on_submit():

        ###################################################################
        # save icon
        # 
        # CHANGE so new icon does not need to uploaded during editing
        ###################################################################
        epaudio = form.epaudio.data
        filename = secure_filename(epaudio.filename)

        ######################################################
        # Need individual files under data_files
        ######################################################
        epaudio.save(os.path.join(path, 'static/'+str(user.id)+'/'+pod_id, filename))

        ep.epname = form.epname.data
        ep.epnum = form.epnum.data
        ep.epdesc = form.epdesc.data
        ep.eplink = form.eplink.data
        ep.audio_path = filename

        ep.it_sum = form.it_sum.data
        ep.it_subtitle = form.it_subtitle.data
        db.session.commit()

        flash('Congratulations, you edited a podcast episode!')
        #return redirect(url_for('index'))
        return redirect(url_for('podcast', pod_id=pod_id, user_id=user.id))

    return render_template('edit_ep.html', title='Edit Podcast', form=form)


##################################################################################
# EDIT PODCAST
##################################################################################
@app.route('/user/<username>/edit_pod/<pod_id>', methods=['GET', 'POST'])
@login_required
def edit_pod(username,pod_id):

    user = User.query.filter_by(username=username).first_or_404()
    podcast = Podcast.query.filter_by(id=pod_id).first_or_404()

    form = EditPodcastForm(obj=podcast)
    if form.validate_on_submit():

        ###################################################################
        # save icon
        # 
        # CHANGE so new icon does not need to uploaded during editing
        ###################################################################
        podicon = form.podicon.data
        filename = secure_filename(podicon.filename)

        ######################################################
        # Need individual files under data_files
        ######################################################
        podicon.save(os.path.join(path, 'static/'+str(user.id)+'/'+str(podcast.id), filename))

        podcast.author = form.author.data
        podcast.podname = form.podname.data
        podcast.poddesc = form.poddesc.data
        podcast.image_path = filename

        podcast.it_own_name = form.it_own_name.data
        podcast.it_own_email = form.it_own_email.data
        podcast.it_cat = form.it_cat.data
        podcast.it_subcat = form.it_subcat.data
        podcast.it_sum = form.it_sum.data
        podcast.it_subtitle = form.it_subtitle.data
        podcast.it_keys = form.it_keys.data
        podcast.it_explicit = form.it_explicit.data

        db.session.commit()

        # attempt to resize image to be square
        im = Image.open(os.path.join(path, 'static/'+str(user.id)+'/'+str(podcast.id), filename))
        w,h = im.size
        rim = im.resize((min(w,h),min(w,h)))
        rim.save(os.path.join(path, 'static/'+str(user.id)+'/'+str(podcast.id), filename))

        flash('Congratulations, you edited a podcast!')
        #return redirect(url_for('index'))
        return redirect(url_for('profile', pod_id=podcast.id, username=user.username))

    return render_template('edit_pod.html', title='Edit Podcast', form=form)


##################################################################################
# INDEX
##################################################################################
@app.route('/')
@app.route('/<order_by>')
def index(order_by = None):

    # setting the positional argument to None makes it optional
    # cannot change default sort order (cut extra options + engineering)

    if order_by == "author":
        # sort by podcast author
        all_pods = Podcast.query.order_by(Podcast.author).all()

    elif order_by == "name":
        # sort by podcast name
        all_pods = Podcast.query.order_by(Podcast.podname).all()

    else:
        # DEFAULT - sort by podcast buildtime
        all_pods = Podcast.query.order_by(Podcast.buildtime.desc()).all()

    return render_template('index.html', all_pods=all_pods)


##################################################################################
# ABOUT
##################################################################################
@app.route('/about')
def about():

    return render_template('about.html')


###################################################################################
# LOGIN PAGE
##################################################################################
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index', username=user.username)

        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)


###################################################################################
# LOGOUT PAGE
##################################################################################
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


##################################################################################
# PODCAST PROFILE
##################################################################################
@app.route('/<user_id>/<pod_id>')
#@login_required
def podcast(user_id, pod_id):

    if current_user.is_authenticated:
        user = User.query.filter_by(id=user_id).first_or_404()
        podcast = Podcast.query.filter_by(id=pod_id).first_or_404()
        eps = Episode.query.filter_by(pod_id=pod_id).all()

        return render_template('podcast.html', user=user, podcast=podcast, eps=eps)
    else:
        user = None
        podcast = Podcast.query.filter_by(id=pod_id).first_or_404()
        eps = Episode.query.filter_by(pod_id=pod_id).all()

        return render_template('podcast.html', user=user, podcast=podcast, eps=eps)



###################################################################################
# REGISTRATION PAGE
##################################################################################
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)

##################################################################################
# USER PROFILE
##################################################################################
@app.route('/profile')
@app.route('/profile/<order_by>')
@login_required
def profile(order_by = None):

    user = User.query.filter_by(id=current_user.id).first_or_404()
    if order_by != None:
        print("order_by: "+order_by)
    else:
        print("order_by: None")

    if order_by == "author":
        # sort by podcast author
        podcasts = Podcast.query.filter_by(user_id=current_user.id).order_by(Podcast.author).all()

    elif order_by == "name":
        # sort by podcast name
        podcasts = Podcast.query.filter_by(user_id=current_user.id).order_by(Podcast.podname).all()

    else:
        # DEFAULT - sort by podcast buildtime
        podcasts = Podcast.query.filter_by(user_id=current_user.id).order_by(Podcast.buildtime.desc()).all()

    return render_template('user.html', user=user, podcasts=podcasts, web_path=web_path)
