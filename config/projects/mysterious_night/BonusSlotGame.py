import random

class BonusSlotGame:
    """
    Represents the bonus game engine for 'Mysterious Night'.
    Handles bonus spawning, multipliers, and level progression.
    """

    def __init__(self, elementsSpawnrate, multipliersSpawnrate, bonusLevels):
        self.elementsSpawnrate = elementsSpawnrate          
        self.multipliersSpawnrate = multipliersSpawnrate    
        self.bonusLevels = bonusLevels                      
        
    def start(self, scatters, bet, gridSize):

        """
        assignar nivell actual segons scatters amb els que hem entrat

        crear un array de gridSize.cols gridSize.rows buit
        iniciar la conta actual de bonus symbols a 0
        iniciar la conta actual de multiplicador a 0

        començar bucle de spins mentres quedin freespins
            //crides a spin i ens guardem el multiplicador que ha sortit
            //crides a evaluate spin passantli el contador de multiplicador del spin
        quan no quedin freespins si el contador de multiplicador es 0 el ficarem a 1, sino no ho toquem

        multipliquem el bet pel multiplicador que ha quedat
        sortim del bonus

        """

        
        return
    

    def spin(self):
        """
        sinicialitza la conta actual de multiplicador del spin a 0
        per cada posicio de la grid
            Es generara un numero aleatori de que representi un percentatge, i es fa servir per determinar si aquella posicio hi ha una carta back, front, chest o bonus symbols (mirant els percentatges guardats a self.elementsSpawnrate)  
            si toca front, es fa un altre numero aleatori per detyerminar quin multiplicador tindra (mirant els percentatges guardats a self.elementsSpawnrate) i es suma al actual del spin
        restem 1 spin als freespins actuals
        al acabar es fa retunr del multiplicador actual del spin
        """
        return

    def evaluate_spin(self, multiplier):
        """
        es revisa si a la grid actual hi ha algun cofre. Si no nhi ha cap multiplier = 0 (ha dapareixer un cofre perqeu es guardin)

        sumem tots els elements bonus de la grid a la conta actual
            si podem pujar de nivell i tenim suficients bonus acumulats per ferho, reiniciem la conta de bonus (afegim el bonus sybol que toqui si havia overflow ex: lvl 1 4/3 --> lvl2 1/3) actualitzem el nivell i sumem els freespins que toquin dentrada al nou nivell mirant self.bonusLevels

        sumem al multipliertotal el multiplier actual
        """
       
        return    
    
    def __repr__(self):
            return f"<BonusSlotGame Level {self.current_level.level_id}, {self.free_spins} FS>"