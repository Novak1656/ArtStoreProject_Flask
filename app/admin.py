from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from app.data_base import *


class ArtModelView(ModelView):
    column_exclude_list = ['art', ]


class UserModelView(ModelView):
    column_exclude_list = ['avatar', ]


class GalleryModelView(ModelView):
    column_exclude_list = ['art', ]


admin = Admin(name='ADMIN', template_mode='bootstrap3', url='/adwdawuais24s32a3f40/') # Admin(app)
admin.add_view(UserModelView(User, db.session))
admin.add_view(ArtModelView(Art, db.session))
admin.add_view(ModelView(Genre, db.session))
admin.add_view(ModelView(Basket, db.session))
admin.add_view(GalleryModelView(Gallery, db.session))

# сделать ограничение доступа к админке





