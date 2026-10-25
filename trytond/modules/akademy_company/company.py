# This file is part of SAGE Education.   The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.model import ModelSQL, ModelView, fields, Unique
from trytond.transaction import Transaction
from trytond.pyson import Eval, If
from trytond.pool import PoolMeta
from datetime import date

_DEGREE_KINSHIP = [
    # Direct kinship (straight line)
    ('father', 'Father'),
    ('mother', 'Mother'),
    ('stepfather', 'Stepfather'),
    ('stepmother', 'Stepmother'),
    ('son', 'Son'),
    ('daughter', 'Daughter'),
    ('grandmother', 'Grandmother'),
    ('grandfather', 'Grandfather'),
    ('great_grandmother', 'Great grandmother'),
    ('great_grandfather', 'Great grandfather'),

    # Collateral kinship
    ('brother', 'Brother'),
    ('sister', 'Sister'),
    ('uncle', 'Uncle'),
    ('aunt', 'Aunt'),
    ('cousin', 'Cousin'),
    ('nephew', 'Nephew'),
    ('niece', 'Niece'),

    # Affinity or guardianship
    ('legal_guardian', 'Legal Guardian'),
    ('supervisor', 'Supervisor'),
    ('guardian', 'Guardian'),
    ('caregiver', 'Caregiver'),
    ('father_partner', 'Father Partner'),
    ('mother_partner', 'Mother Partner'),
    ('godfather', 'Godfather'),
    ('godmother', 'Godmother'),

    # Other links
    ('family_friend', 'Family Friend'),
    ('responsible', 'Responsible'),
    ('other', 'Other'),
]


class Company(metaclass=PoolMeta):
    'Company'
    __name__ = 'company.company'
    
    party = fields.Many2One(
        'party.party', 'Party', 
        domain=[
            ('is_institution', '=', True)
            ], required=True,
        ondelete='CASCADE')
    student = fields.One2Many('company.student', 'company', 'Students',
        help="Add students to the institution.")


class Employee(metaclass=PoolMeta):
    'Employee'
    __name__ = 'company.employee'
       
    teacher = fields.Boolean(
        'Teacher', 
        help="The entity will be treated as a teacher.")

    @classmethod
    def __setup__(cls):
        super(Employee, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('key', Unique(table, table.party, table.company), 
            u'We were unable to register the new employee; please check if the employee already exists.')
        ]
        cls._order = [('party', 'ASC')]

    @classmethod
    def default_start_date(cls):
        return date.today()  
    

class Student(ModelSQL, ModelView):
    'Student'
    __name__ = 'company.student'

    code = fields.Char('Matriculation Number', size=20,
        help="Student matriculation number.")
    start_date = fields.Date('Start',
        domain=[
                If(
                    (Eval('start_date')) & (Eval('end_date')),
                    ('start_date', '<=', Eval('end_date')),
                    (),
                )
            ], depends={'end_date'},
        required=True, help="Start of training.")
    end_date = fields.Date('End',
        domain=[
                If(
                    (Eval('start_date')) & (Eval('end_date')),
                    ('end_date', '>=', Eval('start_date')),
                    (),
                )
            ], depends=['start_date'],
        help="End of training.")    
    party = fields.Many2One(
        'party.party', 'Entity', 
        required=True, domain=[
            ('is_person', '=', True)
            ], ondelete="RESTRICT",
        help="Student name.")
    company = fields.Many2One(
        'company.company', 'Institution', ondelete="RESTRICT", 
        help="Institution name.")     
    student_supervisor = fields.One2Many('company.student.supervisor', 
        'student', 'Student Supervisor')      
    
    @classmethod
    def __setup__(cls):
        super(Student, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('key', Unique(table, table.party, table.company),
            u'It was not possible to register the new student, please check if the student already exists.')
        ]
        cls._order = [('party', 'ASC')]
        
    @classmethod
    def default_start_date(cls):
        return date.today()

    @staticmethod
    def default_company():
        """
        Defines the default company for new students.
        Otherwise, it uses the company from the context.
        """
                    
        return Transaction().context.get('company')

    def get_rec_name(self, name):
        return self.party.rec_name

    @classmethod
    def search_rec_name(cls, name, clause):
        return [('party.rec_name',) + tuple(clause[1:])]


class StudentSupervisor(ModelSQL, ModelView):
    'Student Supervisor'
    __name__ = 'company.student.supervisor'    
	
    description = fields.Text('Description')
    degree_kinship = fields.Selection(_DEGREE_KINSHIP, 
        string=u'Kinship Degree', required=True)
    phone_number = fields.Char('Phone Number', size=20,
        help="Phone Number")
    is_primary = fields.Boolean('Primary', 
        help='Indicates whether you are the main person in charge.')    
    student = fields.Many2One('company.student', 'Student', required=True)
    party = fields.Many2One('party.party', 'Guardian', required=True)

    @classmethod
    def __setup__(cls):
        super(StudentSupervisor, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints = [
            ('key', Unique(table, table.party, table.student), 
            u'It was not possible to register the new guardian, please check if the guardian is already associated with the student.')
        ]

    def get_rec_name(self, name):
        return self.party.rec_name

    @classmethod
    def search_rec_name(cls, name, clause):
        return [('party.rec_name',) + tuple(clause[1:])]
