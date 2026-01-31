# Odoo 19 Mixins Guide

Guide for using Odoo 19 mixins: mail.thread, activities, email aliases, and other useful mixins.

## Table of Contents
- [Messaging Features](#messaging-features)
- [Activities](#activities)
- [Email Aliases](#email-aliases)
- [UTM Mixin](#utm-mixin)
- [Website Mixins](#website-mixins)
- [Rating Mixin](#rating-mixin)

---

## Messaging Features

### Basic Messaging Integration

Add `mail.thread` mixin to your model:

```python
class BusinessTrip(models.Model):
    _name = 'business.trip'
    _inherit = ['mail.thread']
    _description = 'Business Trip'

    name = fields.Char()
    partner_id = fields.Many2one('res.partner', 'Responsible')
    guest_ids = fields.Many2many('res.partner', 'Participants')
```

Add chatter to form view:

```xml
<form string="Business Trip">
    <!-- Your form fields here -->
    <chatter open_attachments="True"/>
</form>
```

### Chatter Options

| Option | Description |
|--------|-------------|
| `open_attachments` | Shows attachment section expanded |
| `reload_on_attachment` | Reload form on attachment change |
| `reload_on_follower` | Reload form on follower update |
| `reload_on_post` | Reload form on message post |

---

### Posting Messages

#### message_post

Post a new message in an existing thread:

```python
record.message_post(
    body='This is a message',
    subject='Subject',
    message_type='notification',
    subtype_xmlid='mail.mt_comment',
)
```

**Parameters**:
- `body` (str | Markup): Message body (escaped if str, use Markup for HTML)
- `subject` (str): Message subject
- `message_type` (str): `notification`, `comment`, `email`
- `subtype` (str/xmlid): Message subtype
- `parent_id` (int): Reply to message
- `attachments` (list): List of `(name, content)` tuples
- `**kwargs`: Extra mail.message field values

#### message_post_with_view

Send message using a QWeb template:

```python
record.message_post_with_view(
    'my_module.my_template',
    additional_context={'val': value},
)
```

#### message_post_with_template

Send message using an email template:

```python
record.message_post_with_template(
    template_id,
    composition_mode='comment',
)
```

---

### Receiving Messages

#### message_new

Called when new email arrives for an alias:

```python
def message_new(self, msg_dict, custom_values=None):
    # Extract data from email
    name = msg_dict.get('subject', 'New')
    # Create record
    return super().message_new(msg_dict, {
        'name': name,
        **(custom_values or {}),
    })
```

#### message_update

Called when email reply arrives:

```python
def message_update(self, msg_dict, update_vals=None):
    # Update record from email
    return super().message_update(msg_dict, {
        'description': msg_dict.get('body'),
        **(update_vals or {}),
    })
```

---

### Followers Management

#### message_subscribe

Add partners/channels as followers:

```python
# Subscribe partners
record.message_subscribe(partner_ids=[pid1, pid2])

# Subscribe channels
record.message_subscribe(channel_ids=[cid1])

# With specific subtypes
record.message_subscribe(
    partner_ids=[pid1],
    subtype_ids=[subtype_id],
)
```

#### message_unsubscribe

Remove followers:

```python
# Unsubscribe partners
record.message_unsubscribe(partner_ids=[pid1, pid2])

# Unsubscribe current user
record.message_unsubscribe_users()
```

---

### Logging Changes (Tracking)

Enable field tracking in `mail.thread`:

```python
class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['mail.thread']

    name = fields.Char(tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
    ], tracking=True)

    # Track changes in relational field
    partner_id = fields.Many2one('res.partner', tracking=1)
```

Track changes in specific subfields:

```python
# Track all partner_id subfields
partner_id = fields.Many2one('res.partner', tracking=True)

# Track only name
partner_id = fields.Many2one('res.partner', tracking='name')
```

---

## Activities

### mail.activity.mixin

Add activity support:

```python
class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['mail.activity.mixin']

    name = fields.Char()
```

### Activity Methods

```python
# Schedule activity
record.activity_schedule(
    'mail.mail_activity_data_todo',
    user_id=user.id,
    summary='Review this',
)

# Mark as done
activities = record.activity_ids
activities.action_done()

# Feedback
activities.action_feedback(feedback='Completed')
```

---

## Email Aliases

### mail.alias.mixin

Add email alias support:

```python
class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['mail.alias.mixin', 'mail.thread']

    name = fields.Char()
    alias_id = fields.Many2one(
        'mail.alias',
        string='Alias',
        ondelete="cascade",
        required=True,
    )

    def get_alias_model_name(self, vals):
        return self._name

    def get_alias_values(self):
        values = super().get_alias_values()
        values.update({
            'alias_defaults': 'name',
        })
        return values
```

Create alias in data file:

```xml
<record id="my_alias" model="mail.alias">
    <field name="alias_name">my-model</field>
    <field name="alias_model_id" ref="model_my_model"/>
    <field name="alias_user_id" ref="base.user_admin"/>
</record>
```

---

## UTM Mixin

### utm.mixin

Add campaign tracking:

```python
class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['utm.mixin']

    name = fields.Char()
    campaign_id = fields.Many2one('utm.campaign', 'Campaign')
    source_id = fields.Many2one('utm.source', 'Source')
    medium_id = fields.Many2one('utm.medium', 'Medium')
```

This adds tracking for marketing campaigns.

---

## Website Mixins

### website.published.mixin

Add website publishing:

```python
class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['website.published.mixin']

    name = fields.Char()
    website_published = fields.Boolean('Visible on Website')
```

### website.seo.metadata

Add SEO metadata:

```python
class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['website.seo.metadata']

    name = fields.Char()
    website_meta_title = fields.Char('Meta Title')
    website_meta_description = fields.Text('Meta Description')
```

---

## Rating Mixin

### rating.mixin

Add customer rating:

```python
class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['rating.mixin', 'mail.thread']

    name = fields.Char()
```

### Rating Methods

```python
# Send rating request
record.rating_send_request(
    rating_template='mail.mail_template_data_rating',
)

# Get rating stats
avg_rating = record.rating_get_stats()
```

---

## Portal Access

### portal.mixin

Add customer portal access:

```python
class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['portal.mixin']

    name = fields.Char()
    partner_id = fields.Many2one('res.partner', 'Customer')
```

Override access:

```python
def _compute_access_url(self):
    super()._compute_access_url()
    for record in self:
        record.access_url = '/my/model/%s' % record.id

def _get_portal_return_action(self):
    return self.env.ref('my_module.my_model_action')
```

---

## References

- Source: Odoo 19 documentation `/doc/developer/reference/backend/mixins.rst`
