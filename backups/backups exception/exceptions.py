class Vortal(Exception):
    class LackInfo(Exception):
        pass
    
    class IncorrectLoginInformation(Exception):
        pass
    
    class GeneralError(Exception):
        pass
    
    class PermissionError(Exception):
        pass
    
    class Requests(Exception):
        class AccessDenied(Exception):
            pass
        
    class Timetable(Exception):
        class MissingLessonID(Exception):
            pass
        
class UserException(Exception):
    class Cache(Exception):
        class UserDoesNotExist(Exception):
            pass
    
    class GoogleAPI(Exception):
        class AuthenticationTimeout(Exception):
            pass
        
        