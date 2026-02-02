# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': 'Portal User Chatter',
    'category': 'Services',
    'version': '18.0.0.1',
    'author': 'TechUltra Solutions Private Limited',
    'company': 'TechUltra Solutions Private Limited',
    'website': "https://www.techultrasolutions.com/",
    'summary': """
    This Odoo module enhances communication by enabling portal users to chat directly with internal users and other portal users. With the "Portal Can Message" option enabled for internal users, portal users can initiate conversations, send and receive messages in real-time, and view the online status of other users. This real-time messaging feature streamlines communication, making collaboration more efficient and seamless within the Odoo platform.
    Odoo portal messaging
    Real-time chat Odoo
    Odoo portal user communication
    Internal user chat Odoo
    Odoo messaging module
    Odoo portal chat feature
    Chat with internal users Odoo
    Odoo chat integration
    Odoo portal direct messaging
    Online status Odoo messaging
    Portal user real-time chat
    Odoo messaging for portal users
    Odoo portal user interaction
    Real-time messaging Odoo portal
    Odoo communication tools portal
    """,
    'description': """
        This module enhances the communication capabilities of Odoo by enabling portal users to chat directly with internal users and other portal users. With the "Portal Can Message" option enabled for internal users, portal users can initiate conversations, send and receive messages in real-time, and view the online status of other users. 
          Odoo portal messaging
    Real-time chat Odoo
    Odoo portal user communication
    Internal user chat Odoo
    Odoo messaging module
    Odoo portal chat feature
    Chat with internal users Odoo
    Odoo chat integration
    Odoo portal direct messaging
    Online status Odoo messaging
    Portal user real-time chat
    Odoo messaging for portal users
    Odoo portal user interaction
    Real-time messaging Odoo portal
    Odoo communication tools portal
    """,
    'category': 'tool',
    'license': 'LGPL-3',
    'depends': ['website', 'web', 'mail', 'im_livechat'],
    # 'depends': ['website', 'web', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/res_user.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            'web/static/src/views/fields/file_handler.*',
            'web/static/src/views/fields/formatters.js',
            'web/static/src/webclient/navbar/navbar.xml',
            'web/static/src/webclient/navbar/navbar.js',
            'web/static/lib/bootstrap/scss/_variables.scss',
            ('include', 'web._assets_bootstrap_backend'),
            'web/static/src/scss/bootstrap_overridden.scss',

            'mail/static/src/model/**/*',
            'mail/static/src/core/common/**/*',
            'mail/static/src/core/common/store_service.js',
            'mail/static/src/discuss/core/common/*',
            'mail/static/src/discuss/call/common/**',
            'mail/static/src/discuss/typing/**/*',
            'mail/static/src/utils/common/**/*',
            'mail/static/src/discuss/core/common/**/*',
            'mail/static/src/discuss/call/common/**/*',
            'mail/static/src/discuss/typing/**/*',

            'mail/static/src/core/public_web/discuss_app_model.js',
            'mail/static/src/core/public_web/discuss_app_category_model.js',
            'mail/static/src/core/public_web/store_service_patch.js',
            'mail/static/src/core/public_web/thread_model_patch.js',
            'mail/static/src/core/public_web/out_of_focus_service_patch.js',

            ('remove', 'mail/static/src/**/*.dark.scss'),
            'web/static/lib/odoo_ui_icons/style.css',
            'web/static/src/scss/ui.scss',
            'web/static/src/core/browser/title_service.js',

            'mail/static/src/core/web/store_service_patch.js',
            'website_portal_chat/static/src/js/messaging_menu_patch.js',
            'mail/static/src/core/web/messaging_menu_patch.xml',
            'mail/static/src/core/web/messaging_menu_patch.scss',
            'mail/static/src/core/web/messaging_menu_quick_search.js',
            'mail/static/src/core/web/messaging_menu_quick_search.xml',

            'mail/static/src/core/public_web/messaging_menu.js',
            'mail/static/src/core/public_web/messaging_menu.xml',
            'mail/static/src/core/public_web/messaging_menu.scss',

            'mail/static/src/discuss/core/public_web/store_service_patch.js',
            'mail/static/src/discuss/core/web/discuss_core_web_service.js',
            'mail/static/src/discuss/core/web/channel_selector.js',
            'mail/static/src/discuss/core/web/channel_selector.xml',
            'mail/static/src/discuss/core/web/chat_window_patch.js',
            'mail/static/src/discuss/core/web/messaging_menu_patch.js',
            'mail/static/src/discuss/core/web/messaging_menu_patch.xml',
            'mail/static/src/discuss/core/web/store_service_patch.js',
            'mail/static/src/discuss/core/web/chat_window_patch.xml',
            'mail/static/src/discuss/core/web/thread_model_patch.js',

            'mail/static/src/core/public_web/notification_item.js',
            'mail/static/src/core/public_web/notification_item.scss',
            'mail/static/src/core/public_web/notification_item.xml',
            'mail/static/src/core/public_web/notification_item.dark.scss',

            'website_portal_chat/static/src/xml/messaging_menu_patch.xml',
            'website_portal_chat/static/src/js/portal_service.js',
            'website_portal_chat/static/src/js/channel_selector.js',
            'website_portal_chat/static/src/js/dropdow_fix.js',
            'website_portal_chat/static/src/css/style.css',
            'website_portal_chat/static/src/scss/new_style.scss'
        ],
        'im_livechat.assets_embed_core': [
            # 'website_portal_chat/static/src/embed/common/chat_window_patch.js',
            ('replace', 'im_livechat/static/src/embed/common/chat_window_patch.js', 'website_portal_chat/static/src/embed/common/chat_window_patch.js'),

        ],
    },
    "images": [
        "static/description/main_screen.gif",
    ],
    'price': 30.99,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,
    'application': True,
}