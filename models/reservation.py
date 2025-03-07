from odoo import fields, models, api
from odoo.exceptions import UserError
from datetime import timedelta

class Reservation(models.Model):
    _name = "my_module.reservation"
    _description = "Liste des réservations faites"
    _inherit = ['mail.thread', 'mail.activity.mixin']


    salle_id = fields.Many2one(
        'my_module.salle', 
        string="Salle de réunion", 
        ondelete="cascade"
    )
    salle_id = fields.Many2one(
        'my_module.salle', 
        string="Salle de réunion", 
        ondelete="cascade"
    )
    etage = fields.Integer("Etage", required=True, tracking=True)
    capacite = fields.Integer("Capacité maximale", required=True, tracking=True)
    qr_code = fields.Binary(string='QR Code', readonly=True)

    # Champ pour suivre les réunions planifiées
    reunion_ids = fields.One2many(
        'my_module.reunion', 
        'salle_id', 
        string="Réunions programmées"
    )
    
    # Statut de la salle (active/inactive)
    active = fields.Boolean(default=True, tracking=True)
    
    # Description ou commentaires supplémentaires
    description = fields.Text("Description")