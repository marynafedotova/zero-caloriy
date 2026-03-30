import os

def get_loko_branch_id(syrve_terminal_id):
    """
    Повертає Loko Branch ID за нашим внутрішнім UUID терміналу.
    """

    loko_locations = {
        str(os.getenv("TERMINAL_RETROVILLE")): os.getenv("LOKO_BRANCH_RETROVILLE"),
        str(os.getenv("TERMINAL_RAJON")): os.getenv("LOKO_BRANCH_RAJON"),
    }
    

    target_id = str(syrve_terminal_id)
    
    return loko_locations.get(target_id)