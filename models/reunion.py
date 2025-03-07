from odoo import fields, models, api
from odoo.exceptions import UserError
from datetime import timedelta

class Reunion(models.Model):
    _name = "my_module.reunion"
    _description = "Un module qui permet aux employés d'organiser, planifier et suivre leurs réunions directement depuis Odoo."
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Inherit from mail.thread and mail.activity.mixin
    event_id = fields.Many2one('calendar.event', string="Événement Calendrier")

    name = fields.Char("Nom", required=True, tracking=True)
    responsable = fields.Many2one('res.partner', string="Responsable", tracking=True)
    sujet = fields.Char("Sujet", required=True, tracking=True)
    description = fields.Char("Descriptions", required=True)
    participants = fields.Many2many('hr.employee', string="Participants")
    lien = fields.Char("Lien", required=False)
    salle_id = fields.Many2one(
        'my_module.salle', 
        string="Salle de réunion", 
        ondelete="cascade"
    )
    type = fields.Selection([
        ('online', 'En ligne'),
        ('meeting', 'En présentiel')
    ], string="Type", required=True, default="meeting", tracking=True)
    date = fields.Datetime("Date", required=True, tracking=True)
    departement = fields.Many2one("hr.department", string="Département", tracking=True, required=True)
    departement_name = fields.Char(related="departement.name", store=True)
    
    # State field with tracking
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmé'),
        ('done', 'Terminé'),
        ('cancelled', 'Annulé')
    ], string="État", default='draft', tracking=True)
    
    duree = fields.Float("Durée", help="Durée estimée de la réunion", required=True, tracking=True)
    # Optional notes
    notes = fields.Html("Notes post-réunion")
    # salle = fields.Char("Salle de réunion")
    visioconference_tool = fields.Selection([
        ('teams', 'Microsoft Teams'),
        ('zoom', 'Zoom'),
        ('google_meet', 'Google Meet'),
        ('other', 'Autre')
    ], string="Outil de Visioconférence", 
      help="Outil utilisé pour la réunion en ligne", 
      states={'online': [('required', True)]})

    message_follower_ids = fields.Many2many(
        'mail.followers', 
        string='Followers', 
        copy=False
    )
    message_ids = fields.One2many(
        'mail.message', 
        'res_id', 
        string='Messages', 
        domain=lambda self: [('model', '=', self._name)],
        auto_join=True,
        copy=False
    )
    activity_ids = fields.One2many(
        'mail.activity', 
        'res_id', 
        string='Activities',
        domain=lambda self: [('res_model', '=', self._name)],
        copy=False
    )

    # field to compute the number of related calendar events
    calendar_event_count = fields.Integer(compute='_compute_calendar_event_count')

    def _compute_calendar_event_count(self):
        for record in self:
            record.calendar_event_count = self.env['calendar.event'].search_count([
                ('name', '=', record.name),
                ('start', '=', record.date)
            ])

    def create_calender_event(self):
        """Marquer la réunion comme terminée"""
        for record in self:
            if record.state == 'done':
                # create calendar event
                event = self.env['calendar.event'].create({
                    'name': record.name,
                    'start': record.date,
                    'stop': record.date + timedelta(hours=record.duree),
                    'duration': record.duree,
                    'location': record.salle_id.name if record.salle_id else False,
                    'videocall_location': record.lien if record.type == 'online' else False,
                    'partner_ids': [(6, 0, record.participants.mapped('user_id.partner_id').ids)],
                    'description': record.description,
                    'user_id': record.responsable.id if record.responsable else self.env.user.id,
                })
                record.event_id = event.id
            else:
                raise UserError("Seules les réunions confirmées peuvent être marquées comme terminées.")

    # Check whether the 'Salle' is available or not (should be active and capacity is convenient for the list of all the participants)
    @api.constrains('salle_id', 'date', 'duree', 'type', 'state')
    def _check_salle(self):
        """Validation de la capacité et disponibilité de la salle"""
        for record in self:
            # Only check for onsite meetings with a selected room
            if record.type != 'meeting' or not record.salle_id or record.state == 'cancelled':
                continue
                
            # Check capacity
            participant_count = len(record.participants)
            if record.salle_id.capacite < participant_count:  # Fixed the comparison operator
                raise UserError("La capacité de la salle n'est pas convenable. Veuillez changer de salle.")
            
            start_time = record.date
            end_time = start_time + timedelta(hours=record.duree)
            
            # Search for conflicting meetings
            conflicting_meetings = self.env['my_module.reunion'].search([
                ('id', '!=', record.id),
                ('salle_id', '=', record.salle_id.id),
                ('type', '=', 'meeting'),
                ('state', 'in', ['draft', 'confirmed','done']),
                ('date', '<', end_time),  
                ('date', '>=', start_time), 
            ])
            # conflicting_meetings = self.env['my_module.reunion'].search(domain)
            print(f"Conflicting meetings found: {len(conflicting_meetings)}")

            if conflicting_meetings :
                raise UserError(f"La salle {record.salle_id.name} est déjà réservée à cette date et heure. Veuillez choisir un autre créneau ou une autre salle.")

    @api.onchange('departement')
    def _onchange_department_id(self):
        """Remplit automatiquement la liste des participants en fonction du département choisi"""
        if self.departement:
            self.participants = self.env['hr.employee'].search([('department_id', '=', self.departement.id)])

    # Action methods for state changes
    def action_confirm(self):
        """Confirmer la réunion"""
        for record in self:
            if record.state == 'draft':
                record.state = 'confirmed'
            else:
                raise UserError("Seules les réunions en brouillon peuvent être confirmées.")

    def action_cancel(self):
        """Annuler la réunion"""
        for record in self:
            if record.state in ['draft', 'confirmed']:
                record.state = 'cancelled'
            else:
                raise UserError("Seules les réunions en brouillon ou confirmées peuvent être annulées.")

    def action_done(self):
        """Marquer la réunion comme terminée"""
        for record in self:
            if record.state == 'confirmed':
                record.state = 'done'
                record.create_calender_event()
            else:
                raise UserError("Seules les réunions confirmées peuvent être marquées comme terminées.")

    def action_view_calendar_events(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Calendar Events',
            'res_model': 'calendar.event',
            'view_mode': 'calendar,tree,form',
            'domain': [('name', '=', self.name), ('start', '=', self.date)],
            'context': {'default_name': self.name}
        }
    
    # Override of the write function:
    def write(self, vals):
        """Override the write method to update the associated calendar event"""
        result = super(Reunion, self).write(vals)

        # Update the associated calendar event
        for record in self:

            if record.event_id:
                # Update the calendar event fields
                record.event_id.write({
                    'name': record.name,
                    'start': record.date,
                    'stop': record.date + timedelta(hours=record.duree),
                    'duration': record.duree,
                    'location': record.salle_id.name if record.salle_id else False,
                    'videocall_location': record.lien if record.type == 'online' else False,
                    'partner_ids': [(6, 0, record.participants.mapped('user_id.partner_id').ids)],
                    'description': record.description,
                    'user_id': record.responsable.id if record.responsable else self.env.user.id,
                })

        return result

    def unlink(self):
        for record in self:
            # Delete the associated calendar event
            if record.event_id:
                record.event_id.unlink()
        return super(Reunion, self).unlink()
