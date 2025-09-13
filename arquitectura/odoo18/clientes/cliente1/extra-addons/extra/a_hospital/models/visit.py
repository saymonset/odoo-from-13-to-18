import random
from datetime import datetime, timedelta
from odoo import models, fields, api, _

from odoo.exceptions import ValidationError
from odoo import _


class Visit(models.Model):
    """
    Model representing a patient's visit within the hospital system.

    Visits are associated with patients, doctors, and may include diagnoses.
    This model supports tracking visit status, scheduling, and the assignment
    of doctors, including approvals by senior doctors.

    Fields:
        - patient_id (Many2one): The patient attending the visit.
        - doctor_id (Many2one): The doctor assigned to the visit.
        - initial_doctor_visit (Char): Initial doctor handling the visit.
        - doctor_approved (Char): Doctor who approved the visit, if required.
        - visit_status (Selection): Current status of the visit
        (e.g., scheduled, completed).
        - scheduled_date (Datetime): Scheduled date and time of the visit.
        - visit_date (Datetime): Actual date and time of the visit.
        - notes (Text): Additional notes about the visit.
        - diagnosis_ids (One2many): List of diagnoses made during the visit.
    """
    _name = 'a_hospital.visit'
    _description = 'Patient Visit'

    active = fields.Boolean(default=True)           # Поле для архівування

    patient_id = fields.Many2one(
        comodel_name='a_hospital.patient',
        string='Patient',
        required=True,
    )

    doctor_id = fields.Many2one(
        comodel_name='a_hospital.doctor',
        string='Doctor',
        required=True,
    )

    initial_doctor_visit = fields.Char(
        string="Initial doctor's visit",
        readonly=True,
    )

    doctor_approved = fields.Char(
        string='Doctor approved',
        readonly=True,
    )

    visit_status = fields.Selection(
        [('scheduled', 'Scheduled'),
         ('completed', 'Completed'),
         ('canceled', 'Canceled')],
        required=True,
        default='scheduled',
    )

    scheduled_date = fields.Datetime(
        string="Scheduled Date & Time",
        required=True,
    )

    visit_date = fields.Datetime(
        string="Visit Date & Time",
    )

    notes = fields.Text()

    diagnosis_ids = fields.One2many(
        comodel_name='a_hospital.diagnosis',
        inverse_name='visit_id',
        string='Diagnoses'
    )

    def generate_random_date(self):
        """
        Generates a random date within the next 30 days.
        Returns:
            str: Formatted random date and time string.
        """
        today = datetime.today()
        days_offset = random.randint(0, 30)
        random_date = today + timedelta(days=days_offset)
        return random_date.strftime('%Y-%m-%d %H:%M:%S')

    @api.onchange('visit_date', 'doctor_id', 'visit_status')
    def _onchange_visit_date(self):
        """
        Restricts modification of visit date, doctor, or status
        if the visit is completed and the doctor is an intern.
        Raises:
            ValidationError: If attempting to modify details
            of a completed visit.
        """
        self.ensure_one()
        if self.visit_status == 'completed' and self.doctor_id.is_intern:
            raise ValidationError(_(
                "You cannot modify the scheduled date "
                "or doctor for a completed visit."))

    def unlink(self):
        """
        Prevents deletion of visits that have associated diagnoses.
        Raises:
            ValidationError: If there are diagnoses linked to the visit.
        """
        for visit in self:
            if visit.diagnosis_ids:
                raise ValidationError(_("You cannot delete "
                                      "visits with diagnoses."))
            return super(Visit, self).unlink()  # Викликаємо super

    @api.constrains('active')
    def _check_active(self):
        """
        Restricts archiving visits that have diagnoses.
        Raises:
            ValidationError: If attempting to archive
            a visit with linked diagnoses.
        """
        for visit in self:
            if not visit.active and visit.diagnosis_ids:
                raise ValidationError(_(
                    "Visits with diagnoses cannot be archived. "
                    "Please remove diagnoses before archiving."
                ))

    @api.constrains('patient_id', 'doctor_id', 'scheduled_date')
    def _check_duplicate_visit(self):
        """
        Prevents scheduling multiple visits for the same patient
        with the same doctor on the same day.
        Raises:
            ValidationError: If there are duplicate visits on the same day.
        """
        for visit in self:
            existing_visits = self.env['a_hospital.visit'].search_count([
                ('patient_id', '=', visit.patient_id.id),
                ('doctor_id', '=', visit.doctor_id.id),
                ('scheduled_date', '>=', visit.scheduled_date.date()),
                ('scheduled_date', '<',
                 visit.scheduled_date.date() + timedelta(days=1)),
                ('id', '!=', visit.id)])
            if existing_visits != 0:
                raise ValidationError(_(
                    "A patient cannot have multiple visits "
                    "with the same doctor on the same day."))

    @api.model_create_multi
    def create(self, vals_list):
        """
        Create new visit records with batch support.
        
        Args:
            vals_list (list or dict): List of dictionaries containing the values for creating records.
                                    If a single dict is passed, it is converted to a list.
        
        Returns:
            recordset: Created visit records.
        """
        # Ensure vals_list is a list
        if isinstance(vals_list, dict):
            vals_list = [vals_list]

        # # Process each dictionary in vals_list
        # for vals in vals_list:
        #     if not vals.get('visit_code'):
        #         vals['visit_code'] = self.env['ir.sequence'].next_by_code('hospital.visit') or _('New')

        # Call the parent create method
        return super(Visit, self).create(vals_list)

    @api.constrains('doctor_id', 'visit_status')
    def _onchange_doctor_id(self):
        """
        Sets the doctor's name in the doctor_approved field once
        the visit is completed and approved.
        Raises:
            ValidationError: If attempting to re-approve
            an already approved visit.
        """
        for visit in self:
            if visit.doctor_id:
                doctor = visit.doctor_id

                # Якщо лікар не інтерн і візит завершений
                if not doctor.is_intern and visit.visit_status == 'completed':
                    # Перевірка, чи поле doctor_approved вже заповнено
                    if not visit.doctor_approved:  # Якщо порожнє або None
                        visit.doctor_approved = doctor.display_name
                    else:
                        raise ValidationError(_(
                            "Doctor has already been "
                            "approved for this visit."))
