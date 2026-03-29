---
name: odoo-18-mixins
description: Complete reference for Odoo 18 mixins and useful classes. Covers mail.thread (messaging, chatter, field tracking), mail.alias.mixin, mail.activity.mixin, utm.mixin, website.published.mixin, website.seo.metadata, and rating.mixin.
globs: "**/models/**/*.py"
topics:
  - mail.thread (messaging, chatter, followers)
  - mail.alias.mixin (email aliases)
  - mail.activity.mixin (activities)
  - utm.mixin (campaign tracking)
  - website.published.mixin (website visibility)
  - website.seo.metadata (SEO)
  - rating.mixin (customer ratings)
when_to_use:
  - Adding messaging/chatter to models
  - Setting up email aliases
  - Adding activities to models
  - Tracking marketing campaigns
  - Creating website-publishable content
  - Implementing customer ratings
---

# Odoo 18 Mixins Guide

Complete reference for Odoo 18 mixins: messaging, email, activities, tracking, website features, and ratings.

## Table of Contents

1. [mail.thread - Messaging](#mailthread---messaging)
2. [mail.alias.mixin - Email Aliases](#mailaliasmixin---email-aliases)
3. [mail.activity.mixin - Activities](#mailactivitymixin---activities)
4. [utm.mixin - Campaign Tracking](#utmmixin---campaign-tracking)
5. [website.published.mixin - Website Visibility](#websitepublishedmixin---website-visibility)
6. [website.seo.metadata - SEO](#websiteseometadata---seo)
7. [rating.mixin - Customer Ratings](#ratingmixin---customer-ratings)

---

## mail.thread - Messaging

### Basic Messaging Integration

The `mail.thread` mixin provides full messaging capabilities: chatter, followers, messages, and field tracking.

#### Minimal Setup

```python
from odoo import models, fields

class BusinessTrip(models.Model):
    _name = 'business.trip'
    _inherit = ['mail.thread']
    _description = 'Business Trip'

    name = fields.Char()
    partner_id = fields.Many2one('res.partner', 'Responsible')
    guest_ids = fields.Many2many('res.partner', 'Participants')
```

#### Form View Integration

```xml
<record id="business_trip_form" model="ir.ui.view">
    <field name="name">business.trip.form</field>
    <field name="model">business.trip</field>
    <field name="arch" type="xml">
        <form string="Business Trip">
            <!-- Your fields -->
            <group>
                <field name="name"/>
                <field name="partner_id"/>
                <field name="guest_ids" widget="many2many_tags"/>
            </group>
            <!-- Chatter integration -->
            <chatter open_attachments="True"/>
        </form>
    </field>
</record>
```

#### Chatter Options

| Option | Description |
|--------|-------------|
| `open_attachments` | Show attachment section expanded by default |
| `reload_on_attachment` | Reload form when attachments change |
| `reload_on_follower` | Reload form when followers change |
| `reload_on_post` | Reload form when messages posted |

### Field Tracking

Automatically log field changes in the chatter.

```python
class BusinessTrip(models.Model):
    _name = 'business.trip'
    _inherit = ['mail.thread']

    name = fields.Char(tracking=True)  # Track changes
    partner_id = fields.Many2one('res.partner', tracking=True)
    guest_ids = fields.Many2many('res.partner')
    state = fields.Selection([
        ('draft', 'New'),
        ('confirmed', 'Confirmed'),
    ], tracking=True)
```

Every change to `name`, `partner_id`, or `state` will log a note in the chatter.

### Posting Messages

#### message_post() - Post a Message

```python
def send_notification(self):
    self.message_post(
        body='Trip has been confirmed!',
        subject='Trip Confirmation',
        message_type='notification',
        subtype_xmlid='mail.mt_comment',
    )
```

#### message_post() with HTML

```python
from markupsafe import Markup

def send_html_notification(self):
    self.message_post(
        body=Markup('<strong>Trip confirmed!</strong>'),
        subject='Trip Confirmation',
    )
```

#### message_post() with Attachments

```python
def send_with_attachment(self):
    self.message_post(
        body='Please review attached document',
        attachments=[
            ('document.pdf', pdf_content),
            ('summary.txt', summary_text),
        ]
    )
```

#### message_post_with_template() - Use QWeb Template

```python
def send_template_email(self):
    self.message_post_with_template(
        template_id=self.env.ref('my_module.email_template').id,
    )
```

### Followers Management

#### message_subscribe() - Add Followers

```python
# Add partners
record.message_subscribe(
    partner_ids=[partner1_id, partner2_id]
)

# Add channels
record.message_subscribe(
    channel_ids=[channel1_id, channel2_id]
)

# Add with specific subtypes
record.message_subscribe(
    partner_ids=[partner_id],
    subtype_ids=[self.env.ref('mail.mt_comment').id]
)

# Force: remove existing followers first
record.message_subscribe(
    partner_ids=[new_partner_id],
    force=True
)
```

#### message_unsubscribe() - Remove Followers

```python
# Remove partners
record.message_unsubscribe(partner_ids=[partner_id])

# Remove channels
record.message_unsubscribe(channel_ids=[channel_id])

# Remove users
record.message_unsubscribe_users(user_ids=[user_id])
```

### Subtypes - Notification Control

Subtypes classify notifications, allowing users to customize what they receive.

#### Creating a Subtype

```xml
<record id="mt_state_change" model="mail.message.subtype">
    <field name="name">Trip Confirmed</field>
    <field name="res_model">business.trip</field>
    <field name="default" eval="True"/>
    <field name="description">Business Trip confirmed!</field>
    <field name="internal" eval="False"/>
</record>
```

#### Subtype Fields

| Field | Description |
|-------|-------------|
| `name` | Display name in notification popup |
| `description` | Message added when posted |
| `internal` | If `True`, only visible to employees |
| `parent_id` | Link to parent subtype (for auto-subscription) |
| `relation_field` | Field linking to parent (e.g., `project_id`) |
| `res_model` | Model this applies to (`False` = all models) |
| `default` | Activated by default when subscribing |
| `hidden` | Hidden in notification customization popup |

#### _track_subtype() - Trigger Specific Subtype

```python
class BusinessTrip(models.Model):
    _name = 'business.trip'
    _inherit = ['mail.thread']

    state = fields.Selection([
        ('draft', 'New'),
        ('confirmed', 'Confirmed'),
    ], tracking=True)

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'confirmed':
            return 'my_module.mt_state_change'
        return super(BusinessTrip, self)._track_subtype(init_values)
```

### Customizing Notifications

#### _notify_get_groups() - Custom Action Buttons

```python
class BusinessTrip(models.Model):
    _name = 'business.trip'
    _inherit = ['mail.thread']

    def action_cancel(self):
        self.write({'state': 'draft'})

    def _notify_get_groups(self, message, groups):
        groups = super(BusinessTrip, self)._notify_get_groups(message, groups)

        self.ensure_one()
        if self.state == 'confirmed':
            cancel_link = self._notify_get_action_link('method', method='action_cancel')
            trip_actions = [{'url': cancel_link, 'title': _('Cancel')}]

        # Add custom group
        new_group = (
            'group_trip_manager',
            lambda partner: any(
                user.sudo().has_group('business.group_trip_manager')
                for user in partner.user_ids
            ),
            {'actions': trip_actions},
        )

        return [new_group] + groups
```

#### _notify_get_action_link() - Generate Links

```python
# View link
view_link = self._notify_get_action_link('view')

# Assign link
assign_link = self._notify_get_action_link('assign')

# Follow/Unfollow
follow_link = self._notify_get_action_link('follow')
unfollow_link = self._notify_get_action_link('unfollow')

# Custom method
method_link = self._notify_get_action_link('method', method='action_do_something')

# New record
new_link = self._notify_get_action_link('new', action_id='action_id')
```

### Context Keys for Control

| Key | Effect |
|-----|--------|
| `mail_create_nosubscribe` | Don't subscribe current user on create |
| `mail_create_nolog` | Don't log 'Document created' message |
| `mail_notrack` | Don't perform value tracking |
| `tracking_disable` | Disable all MailThread features |
| `mail_auto_delete` | Auto delete notifications (default: `True`) |
| `mail_notify_force_send` | Send directly if < 50 emails (default: `True`) |

```python
# Example: create without auto-subscription
record = self.env['business.trip'].with_context(
    mail_create_nosubscribe=True
).create({'name': 'Trip'})
```

### _mail_post_access

Control required access rights to post messages:

```python
class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['mail.thread']

    _mail_post_access = 'read'  # Default is 'write'
```

---

## mail.alias.mixin - Email Aliases

### Alias Basics

Aliases allow creating records via email without logging into Odoo.

#### Required Overrides

```python
from odoo import models, fields

class BusinessTrip(models.Model):
    _name = 'business.trip'
    _inherit = ['mail.thread', 'mail.alias.mixin']
    _description = 'Business Trip'

    name = fields.Char()
    partner_id = fields.Many2one('res.partner')
    expense_ids = fields.One2many('business.expense', 'trip_id')
    alias_id = fields.Many2one('mail.alias', required=True, ondelete="restrict")

    def _get_alias_model_name(self, vals):
        """Model to create when alias receives email"""
        return 'business.expense'

    def _get_alias_values(self):
        """Default values for the alias"""
        values = super(BusinessTrip, self)._get_alias_values()
        values['alias_defaults'] = {'trip_id': self.id}
        values['alias_contact'] = 'followers'
        return values
```

#### Form View Integration

```xml
<page string="Emails">
    <group name="group_alias">
        <label for="alias_name" string="Email Alias"/>
        <div name="alias_def">
            <field name="alias_id" class="oe_read_only oe_inline" string="Email Alias"/>
            <div class="oe_edit_only oe_inline" style="display: inline;">
                <field name="alias_name" class="oe_inline"/>
                @
                <field name="alias_domain" class="oe_inline" readonly="1"/>
            </div>
        </div>
        <field name="alias_contact" class="oe_inline" string="Accept Emails From"/>
    </group>
</page>
```

### Alias Configuration Fields

| Field | Description |
|-------|-------------|
| `alias_name` | Email alias name (e.g., 'jobs' for jobs@example.com) |
| `alias_user_id` | Owner of created records |
| `alias_defaults` | Python dict of default values |
| `alias_force_thread_id` | If set, all messages go to this thread |
| `alias_contact` | Who can post: `everyone`, `partners`, `followers` |
| `alias_domain` | Email domain (automatic from system) |

### message_new() - Handle Incoming Emails

Override to extract data from incoming emails:

```python
class BusinessExpense(models.Model):
    _name = 'business.expense'
    _inherit = ['mail.thread']

    amount = fields.Float()
    description = fields.Char()
    partner_id = fields.Many2one('res.partner')

    def message_new(self, msg_dict, custom_values=None):
        """Extract data from email"""
        name = msg_dict.get('subject', 'New Expense')

        # Extract amount from subject (last float)
        import re
        amount_pattern = r'(\d+(?:\.\d*)?)'
        prices = re.findall(amount_pattern, name)
        amount = float(prices[-1]) if prices else 0.0

        # Find partner by email
        email = msg_dict.get('from')
        partner = self.env['res.partner'].search([
            ('email', 'ilike', email)
        ], limit=1)

        defaults = {
            'name': name,
            'amount': amount,
            'partner_id': partner.id
        }
        defaults.update(custom_values or {})
        return super(BusinessExpense, self).message_new(msg_dict, defaults)
```

### message_update() - Handle Email Replies

```python
def message_update(self, msg_dict, update_vals=None):
    """Update record from email reply"""
    # Extract data and update
    if 'description' in msg_dict:
        update_vals = update_vals or {}
        update_vals['description'] = msg_dict['description']
    return super(BusinessExpense, self).message_update(msg_dict, update_vals)
```

---

## mail.activity.mixin - Activities

### Activity Integration

Activities are actions users need to take (phone calls, meetings, etc.).

```python
from odoo import models, fields

class BusinessTrip(models.Model):
    _name = 'business.trip'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Business Trip'

    name = fields.Char()
```

#### Form View Integration

```xml
<form string="Business Trip">
    <!-- Your fields -->
    <chatter>
        <field name="message_follower_ids" widget="mail_followers"/>
        <field name="activity_ids" widget="mail_activity"/>
        <field name="message_ids" widget="mail_thread"/>
    </chatter>
</form>
```

#### Kanban View Integration

```xml
<kanban>
    <field name="activity_ids"/>
    <field name="activity_state"/>
    <templates>
        <t t-name="kanban-box">
            <div>
                <!-- Your content -->
                <div class="oe_kanban_activity"/>
            </div>
        </t>
    </templates>
</kanban>
```

### Activity Methods

The mixin provides these methods:

| Method | Description |
|--------|-------------|
| `activity_schedule()` | Schedule an activity |
| `activity_unlink()` | Remove activities |
| `action_feedback()` | Add feedback to activity |

```python
# Schedule activity
record.activity_schedule(
    'mail.mail_activity_data_todo',
    user_id=user_id,
    summary='Review trip',
    note='Please review and approve',
    date_deadline=date.today()
)

# Mark as done
record.action_feedback(
    feedback='Approved!',
    feedback_type='done'
)
```

---

## utm.mixin - Campaign Tracking

### UTM Tracking

Track marketing campaigns through URL parameters (campaign, source, medium).

```python
from odoo import models, fields

class Lead(models.Model):
    _name = 'crm.lead'
    _inherit = ['utm.mixin']
    _description = 'Lead'

    name = fields.Char()
```

#### Added Fields

| Field | Type | Description |
|-------|------|-------------|
| `campaign_id` | Many2one | UTM Campaign (e.g., Christmas_Special) |
| `source_id` | Many2one | UTM Source (e.g., Search Engine) |
| `medium_id` | Many2one | UTM Medium (e.g., Email, Social Network) |

#### How It Works

1. User visits: `https://myodoo.com/?campaign_id=winter_sale&source_id=google`
2. Cookies are set for these parameters
3. When a record is created from website form, values are fetched from cookies
4. Campaign/source/medium fields are automatically populated

### Extending UTM Tracking

```python
class MyTrack(models.Model):
    _name = 'my.track'
    _description = 'Custom Tracking'

    name = fields.Char(required=True)

class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['utm.mixin']

    my_field = fields.Many2one('my.track', 'My Field')

    @api.model
    def tracking_fields(self):
        result = super(MyModel, self).tracking_fields()
        result.append([
            # ("URL_PARAMETER", "FIELD_NAME_MIXIN", "COOKIE_NAME")
            ('my_field', 'my_field', 'odoo_utm_my_field')
        ])
        return result
```

This creates a cookie `odoo_utm_my_field` and sets `my_field` on new records.

---

## website.published.mixin - Website Visibility

### Website Publishing

Control whether records are visible on the website.

```python
from odoo import models, fields

class BlogPost(models.Model):
    _name = 'blog.post'
    _inherit = ['website.published.mixin']
    _description = 'Blog Post'

    name = fields.Char()
    website_url = fields.Char()  # Must be defined

    def _compute_website_url(self):
        for post in self:
            post.website_url = f"/blog/{post.id}"
```

#### Added Fields

| Field | Type | Description |
|-------|------|-------------|
| `website_published` | Boolean | Publication status |
| `website_url` | Char | URL to access the record |

#### Backend Button

```xml
<div name="button_box">
    <button class="oe_stat_button" name="website_publish_button" type="object" icon="fa-globe">
        <field name="website_published" widget="website_button"/>
    </button>
</div>
```

#### Frontend Button

```xml
<div id="website_published_button" class="float-right" groups="base.group_website_publisher">
    <t t-call="website.publish_management">
        <t t-set="object" t-value="blog_post"/>
        <t t-set="publish_edit" t-value="True"/>
        <t t-set="action" t-value="'blog.blog_post_action'"/>
    </t>
</div>
```

---

## website.seo.metadata - SEO

### SEO Metadata

Inject metadata into frontend pages for search engines.

```python
from odoo import models, fields

class BlogPost(models.Model):
    _name = 'blog.post'
    _inherit = ['website.seo.metadata', 'website.published.mixin']
    _description = 'Blog Post'

    name = fields.Char()
```

#### Added Fields

| Field | Type | Description |
|-------|------|-------------|
| `website_meta_title` | Char | Additional page title |
| `website_meta_description` | Char | Short description for search results |
| `website_meta_keywords` | Char | Keywords for search engine classification |

These fields are editable via the "Promote" tool in the website editor.

---

## rating.mixin - Customer Ratings

### Rating Integration

Allow sending rating requests and aggregating statistics.

```python
from odoo import models, fields

class ProjectTask(models.Model):
    _name = 'project.task'
    _inherit = ['rating.mixin', 'mail.thread']
    _description = 'Task'

    name = fields.Char()
    user_id = fields.Many2one('res.users', 'Responsible')
    partner_id = fields.Many2one('res.partner', 'Customer')
```

#### Behavior

The mixin automatically:
- Links `rating.rating` records to `partner_id` field (if exists)
- Links to `user_id` partner (if exists)
- Displays rating events in chatter (if inherits `mail.thread`)

#### Override Partner Fields

```python
class MyModel(models.Model):
    _inherit = ['rating.mixin', 'mail.thread']

    def rating_get_partner_id(self):
        """Override to use different field"""
        return self.my_custom_partner_id

    def rating_get_rated_partner_id(self):
        """Override to specify who is being rated"""
        return self.user_id.partner_id
```

### Send Rating Request Email

```xml
<record id="rating_email_template" model="mail.template">
    <field name="name">Rating Request</field>
    <field name="subject">Service Rating</field>
    <field name="model_id" ref="model_my_model"/>
    <field name="partner_to">${object.rating_get_partner_id().id}</field>
    <field name="auto_delete" eval="True"/>
    <field name="body_html"><![CDATA[
        % set access_token = object.rating_get_access_token()
        <p>How satisfied are you?</p>
        <ul>
            <li><a href="/rate/${access_token}/5">Satisfied</a></li>
            <li><a href="/rate/${access_token}/3">Okay</a></li>
            <li><a href="/rate/${access_token}/1">Dissatisfied</a></li>
        </ul>
    ]]></field>
</record>
```

### Rating Action

```xml
<record id="rating_action" model="ir.actions.act_window">
    <field name="name">Customer Ratings</field>
    <field name="res_model">rating.rating</field>
    <field name="view_mode">kanban,pivot,graph</field>
    <field name="domain">[
        ('res_model', '=', 'my.model'),
        ('res_id', '=', active_id),
        ('consumed', '=', True)
    ]</field>
</record>
```

#### Add Rating Button

```xml
<xpath expr="//div[@name='button_box']" position="inside">
    <button name="%(rating_action)d" type="action" class="oe_stat_button" icon="fa-smile-o">
        <field name="rating_count" string="Rating" widget="statinfo"/>
    </button>
</xpath>
```

---

## Quick Reference

### Mixin Comparison

| Mixin | Purpose | Key Features |
|-------|---------|--------------|
| `mail.thread` | Messaging | Chatter, followers, field tracking |
| `mail.alias.mixin` | Email | Create records via email |
| `mail.activity.mixin` | Activities | Schedule activities |
| `utm.mixin` | Marketing | Campaign tracking |
| `website.published.mixin` | Website | Publish/unpublish toggle |
| `website.seo.metadata` | SEO | Meta title, description, keywords |
| `rating.mixin` | Ratings | Customer feedback system |

### Common Combinations

```python
# Standard document model
_inherit = ['mail.thread']

# Document with activities
_inherit = ['mail.thread', 'mail.activity.mixin']

# Website content
_inherit = ['website.published.mixin', 'website.seo.metadata']

# Model with email processing
_inherit = ['mail.thread', 'mail.alias.mixin']

# CRM-style model
_inherit = ['mail.thread', 'mail.activity.mixin', 'utm.mixin', 'rating.mixin']

# Full-featured website model
_inherit = ['mail.thread', 'mail.activity.mixin', 'website.published.mixin',
            'website.seo.metadata', 'utm.mixin']
```

---

**For more Odoo 18 guides, see [SKILL.md](../SKILL.md)**
