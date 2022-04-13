import logging
from sqlalchemy import Integer, Float, DateTime, String, ForeignKey, Time

from garmindb import ActivityFitPluginBase


logger = logging.getLogger(__file__)


@classmethod
def create_activity_view(cls, act_db):
    """Create a database view for the hrv plugin data."""
    view_selectable = [
        cls.activities_table.activity_id.label('activity_id'),
        cls.activities_table.name.label('name'),
        cls.activities_table.description.label('description'),
        cls.activities_table.start_time.label('start_time'),
        cls.activities_table.stop_time.label('stop_time'),
        cls.activities_table.elapsed_time.label('elapsed_time'),
        cls.min_hr.label('min_hr'),
        cls.hrv_rmssd.label('hrv_rmssd'),
        cls.hrv_sdrr_f.label('hrv_sdrr_f'),
        cls.hrv_sdrr_l.label('hrv_sdrr_l'),
        cls.hrv_pnn50.label('hrv_pnn50'),
        cls.hrv_pnn20.label('hrv_pnn20')
    ]
    view_name = 'test_hrv_activities_view'
    logger.info("Creating hrv plugin view %s if needed.", view_name)
    cls.create_join_view(act_db, view_name, view_selectable, cls.activities_table, order_by=cls.activities_table.start_time.desc())


class test_hrv(ActivityFitPluginBase):

    _application_id = bytearray(b'\x0b\xdc\x0eu\x9b\xaaAz\x8c\x9f\xe9vf*].')

    _records_tablename = 'test_hrv_records'
    _records_version = 1
    _records_pk = ("activity_id", "record")
    _records_cols = {
        'activity_id': {'args': [String, ForeignKey('activities.activity_id')]},
        'record': {'args': [Integer]},
        'timestamp': {'args': [DateTime]},
        # 'stress_hrp': {'args': [Float], 'units': 'bpm'},
        'hrv_s': {'args': [Float], 'units': 'ms'},
        'hrv_btb': {'args': [Integer], 'units': 'ms'},
        'hrv_hr': {'args': [Integer], 'units': 'bpm'},
        'hrv_rmssd30s': {'args': [Float], 'units': 'ms'},
        'stress_hrp': {'args': [Float], 'units': '%'},
    }   


    _sessions_tablename = 'test_hrv_sessions'
    _sessions_version = 1
    _sessions_cols = {
        'activity_id': {'args': [String, ForeignKey('activities.activity_id')], 'kwargs': {'primary_key': True}},
        'timestamp': {'args': [DateTime]},
        'start_time': {'args': [DateTime]},
        'elapsed_time': {'args': [Time]},
        'min_hr': {'args': [Integer], 'units': 'bpm'},
        # 'stress_hrpa': {'args': [Float], 'units': '%'},
        'hrv_rmssd': {'args': [Float], 'units': 'ms'},
        'hrv_sdrr_f': {'args': [Float], 'units': 'ms'},
        'hrv_sdrr_l': {'args': [Float], 'units': 'ms'},
        'hrv_pnn50': {'args': [Float], 'units': '%'},
        'hrv_pnn20': {'args': [Float], 'units': '%'},
}

    _tables = {}
    _views = {'activity_view': create_activity_view}

    def write_record_entry(self, activity_db_session, fit_file, activity_id, message_fields, record_num):
        """Write a record message into the plugin records table."""
        record_table = self._tables['record']
        if not record_table.s_exists(activity_db_session, {'activity_id' : activity_id, 'record' : record_num}):
            record = {
                'activity_id'   : activity_id,
                'record'        : record_num,
                'timestamp'     : fit_file.utc_datetime_to_local(message_fields.timestamp),
                # 'stress_hrp'    : message_fields.get('dev_stress_hrp'),
                'hrv_s'         : message_fields.get('dev_hrv_s'),
                'hrv_btb'       : message_fields.get('dev_hrv_btb'),
                'hrv_rmssd30s'  : message_fields.get('dev_hrv_rmssd30s'),
                'hrv_hr'        : message_fields.get('dev_hrv_hr'),
            }
            logger.debug("writing hrv record %r for %s", record, fit_file.filename)
            activity_db_session.add(record_table(**record))
        return {}

    def write_session_entry(self, activity_db_session, fit_file, activity_id, message_fields):
        """Write a session message into the plugin sessions table."""
        session_table = self._tables['session']
        if not session_table.s_exists(activity_db_session, {'activity_id' : activity_id}):
            session = {
                'activity_id'   : activity_id,
                'timestamp'     : fit_file.utc_datetime_to_local(message_fields.timestamp),
                'start_time'     : fit_file.utc_datetime_to_local(message_fields.start_time),
                'elapsed_time'     : fit_file.utc_datetime_to_local(message_fields.total_elapsed_time),
                'min_hr'        : message_fields.get('dev_min_hr'),
                # 'stress_hrpa'   : message_fields.get('dev_stress_hrpa'),
                'hrv_rmssd'     : message_fields.get('dev_hrv_rmssd'),
                'hrv_sdrr_f'    : message_fields.get('dev_hrv_sdrr_f'),
                'hrv_sdrr_l'    : message_fields.get('dev_hrv_sdrr_l'),
                'hrv_pnn50'     : message_fields.get('dev_hrv_pnn50'),
                'hrv_pnn20'     : message_fields.get('dev_hrv_pnn20'),
            }
            logger.debug("writing hrv session %r for %s", session, fit_file.filename)
            activity_db_session.add(session_table(**session))
        return {}
