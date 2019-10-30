import random
import numpy as np
import pickle
from pickle import UnpicklingError
from pathlib import Path

class ReplayMemory:
    """
    The SAC algorithm uses an experience replay buffer to learn from past samples. This class allows to add transitions 
    to the replay buffer, save the replay buffer, and to sample past transitions from the replay buffer.  
    
    **Parameters**:  
    
    - **capacity** *(int)*:  Defines the size of the replay buffer.
    """
    def __init__(self, capacity):
        self.capacity = capacity
        self.buffer = []
        self.position = 0

    def push(self, state, action, reward, next_state, done):
        """
        Appends a transistion to the replay buffer.  
        
        **Parameters**:  
        
        - **state** *(array)*:  Contains thirty-two float32 values that represent the agent's observable environment before 
        executing its action.
        - **action** *(array)*:  Contains three float32 values that allow to steer, accelerate and decelerate the vehicle.
        - **reward** *(float)*:  Represents the reward that the agent receives from the environment for its action.
        - **next_state** *(array)*:  Contains thirty-two float32 values that represent the agent's observable environment after 
        executing its action.
        - **done** *(boolean)*:  Changes to *True* when the number of tiles that the agent visited euqals the current track's 
        tile count or the agent goes to far astray and consequently aborts the current episode.
        """
        if len(self.buffer) < self.capacity:
            self.buffer.append(None)
        self.buffer[self.position] = (state, action, reward, next_state, done)
        self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size):
        """
        Outputs samples contained in the replay buffer.  
        
        **Parameters**:  
        
        - **batch_size** *(int)*:  Defines how many samples to output.
        
        **Output**:  
        
        - **state** *(array)*: Contains *batch_size* state arrays
        - **action** *(array)*: Contains *batch_size* action arrays
        - **reward** *(array)*: Contains *batch_size* reward values
        - **next_state** *(array)*: Contains *batch_size* next_state arrays
        - **done** *(array)*: Contains *batch_size* done values
        """
        batch = random.sample(self.buffer, batch_size)
        state, action, reward, next_state, done = map(np.stack, zip(*batch))
        return state, action, reward, next_state, done

    def save(self, path: str):
        """
        Option to save the replay buffer to allow to pick up model training in the future. 
        The buffer is saved to path "/memory/buffer" as a Pickle file.
        
        **Parameters**:  
        
        - **path** *(String)*:  Defined as "buffer" in the calling method train().
        """
        print(f"Saving replay buffer to {path}.")
        save_dir = Path("memory/")
        if not save_dir.exists():
            save_dir.mkdir() 
        with open((save_dir/path).with_suffix(".pkl"), "wb") as fp:
            pickle.dump(self.buffer, fp)

    def load(self, path: str):
        """
        Option to load a previously saved replay buffer from a Pickle file.  
        
        ## Parameters:  
        
        - **path** *(String)*:  Path to Pickle file.
        """
        try:
            with open(path, "rb") as fp:
                mem = pickle.load(fp)
                assert len(mem) == self.capacity, "Capacity of the replay buffer and length of the loaded memory don't match!"
                self.buffer = mem
            print(f"Loaded saved replay buffer from {path}.")
        except UnpicklingError:
            raise TypeError("This file doesn't contain a pickled list!")

    def __len__(self):
        return len(self.buffer)
