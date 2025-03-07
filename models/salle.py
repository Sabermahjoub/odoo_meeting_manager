from odoo import fields, models, api
from odoo.exceptions import UserError
from datetime import timedelta
import base64
import qrcode
from io import BytesIO

class Salle(models.Model):
    _name = "my_module.salle"
    _description = "Salles de réunion disponibles dans l'entreprise"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Nom", required=True, tracking=True)
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
    
    reunion_count = fields.Integer(
        compute='_compute_reunion_count', 
        string='Number of Meetings'
    )

    def action_view_reunions(self):
    # Action to view related reunions
        return {
            'name': 'Réunions',
            'type': 'ir.actions.act_window',
            'res_model': 'my_module.reunion',
            'view_mode': 'tree,form',
            'domain': [('salle_id', '=', self.id)],
            'context': {
                'default_salle_id': self.id,
            }
        }
    
    def generate_qr_code(self):
        # Generate QR Code for the room
        for record in self:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(f"Room: {record.name}\nFloor: {record.etage}\nCapacity: {record.capacite}")
            qr.make(fit=True)
            
            # Create an image from the QR Code
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save the image to a bytes buffer
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            
            # Convert to base64
            record.qr_code = base64.b64encode(buffer.getvalue())
        
        # Optional: Return a wizard to show/download the QR code
        return {
            'name': 'QR Code',
            'type': 'ir.actions.act_window',
            'res_model': 'my_module.salle',
            'view_mode': 'form',
            'res_id': self.id,
            'view_type': 'form',
            'target': 'new',
        }

    @api.depends('reunion_ids')
    def _compute_reunion_count(self):
        for record in self:
            record.reunion_count = len(record.reunion_ids)

    @api.constrains('capacite')
    def _check_capacite(self):
        """Validation de la capacité de la salle"""
        for record in self:
            if record.capacite <= 0:
                raise UserError("La capacité de la salle doit être supérieure à zéro.")
    
    def verifier_disponibilite(self, date_debut, duree):
        """
        Vérifie si la salle est disponible pour une réunion donnée
        
        :param date_debut: Datetime de début de la réunion
        :param duree: Durée de la réunion en minutes
        :return: Booléen indiquant la disponibilité
        """
        date_fin = date_debut + timedelta(minutes=duree)
        
        # Recherche de conflits de réservation
        conflits = self.env['my_module.reunion'].search([
            ('salle_id', '=', self.id),
            ('date_debut', '<', date_fin),
            ('date_fin', '>', date_debut)
        ])
        
        return len(conflits) == 0
    
    def get_salles_disponibles(self, date_debut, duree, capacite_requise=0):
        """
        Trouve toutes les salles disponibles pour une réunion
        
        :param date_debut: Datetime de début de la réunion
        :param duree: Durée de la réunion en minutes
        :param capacite_requise: Capacité minimale requise
        :return: Recordset des salles disponibles
        """
        salles_disponibles = self.search([
            ('active', '=', True),
            ('capacite', '>=', capacite_requise)
        ])
        
        return salles_disponibles.filtered(
            lambda salle: salle.verifier_disponibilite(date_debut, duree)
        )

# Modèle optionnel pour les équipements de salle
# class Equipement(models.Model):
#     _name = "my_module.equipement"
#     _description = "Équipements des salles de réunion"
    
#     name = fields.Char("Nom de l'équipement", required=True)
#     description = fields.Text("Description")