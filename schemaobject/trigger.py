from schemaobject.collections import OrderedDict

def TriggerSchemaBuilder(database):
    conn = database.parent.connection

    t = OrderedDict()

    sql = """
            SELECT TRIGGER_NAME, EVENT_MANIPULATION, EVENT_OBJECT_TABLE,
                ACTION_STATEMENT, ACTION_TIMING 
            FROM INFORMATION_SCHEMA.TRIGGERS 
            WHERE TRIGGER_SCHEMA='%s'
        """

    triggers = conn.execute(sql % database.name)

    if not triggers:
        return t

    for trigger in triggers:
        trig_name = trigger['TRIGGER_NAME']
        
        trig = TriggerSchema(name=trig_name, parent=database)
        trig.statement = trigger['ACTION_STATEMENT']
        trig.timing = trigger['ACTION_TIMING']
        trig.event = trigger['EVENT_MANIPULATION']
        trig.table = trigger['EVENT_OBJECT_TABLE']

        t[trig_name] = trig

    return t

class TriggerSchema(object):
    def __init__(self, name, parent):
        self.parent = parent
        self.name = name
        self.statement = None
        self.timing = None
        self.event = None
        self.table = None

    def define(self):
        sql = []
        sql.append("`%s` %s %s ON %s FOR EACH ROW %s" % (self.name, 
                    self.timing, 
                    self.event, 
                    self.table, 
                    self.statement))

        return ' '.join(sql)

    def create(self):
        return "DELIMITER ;; CREATE TRIGGER %s;; DELIMITER ;" % self.define()
   
    def modify(self):
        pass # Need to drop + re-create

    def drop(self):
        return "DROP TRIGGER `%s`;" % self.name

    def __eq__(self,other):
        if not isinstance(other, TriggerSchema):
            return False

        return ((self.name == other.name)
                and (self.statement == other.statement)
                and (self.timing == other.timing)
                and (self.table == other.table)
                and (self.event == other.event))

    def __ne__(self, other):
        return not self._eq__(other)