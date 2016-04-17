
import primes;
import random;
import sys;

class BlumBlumShub(object):


    def getPrime(self, bits):
        """
        Generate appropriate prime number for use in Blum-Blum-Shub.
         
        This generates the appropriate primes (p = 3 mod 4) needed to compute the
        "n-value" for Blum-Blum-Shub.
         
        bits - Number of bits in prime

        """
        while True:
            p = primes.bigppr(bits);
            if p%4 == 3:
                break
        return p

    def generateN(self, bits):
        """
        This generates the "n value" for use in the Blum-Blum-Shub algorithm.
       
        bits - The number of bits of security
        """
    
        p = self.getPrime(bits/2)
        q = self.getPrime(bits/2)

        # make sure p != q (almost always true, but just in case, check)
        while p == q:
            q = getPrime(self, bits/2);
        
        # print "GenerateN - p = " + repr(p) + ", q = " + repr(q)            
        return p * q;
    

    def __init__(self, bits):
        """
        Constructor, specifing bits for n.
         
        bits - number of bits
        """        
        self.n = self.generateN(bits)
        # print "n set to " + repr(self.n)
        length = self.bitLen(self.n)
        seed = random.getrandbits(length)
        self.setSeed(seed)  

    def setSeed(self, seed):
        """
        Sets or resets the seed value and internal state.
         
        seed -The new seed
        """
    
        self.state = seed % self.n
    
    def bitLen(self, x):
        " Get the bit lengh of a positive number" 
        assert(x>0)
        q = 0 
        while x: 
            q = q+1 
            x = x>>1 
        return q     

    def next(self, numBits):
        "Returns up to numBit random bits"
        
        result = 0
        for i in range(numBits,0,-1):
            self.state = (self.state**2) % self.n
            result = (result << 1) | (self.state&1)
        
        return result    

def main():
    
    bbs = BlumBlumShub(128);
        
    #print "Generating 10 numbers"
    
    print "type: u"
    print "numbit: 32"
    print "count: 5000000"
    for i in range (0,5):
        print bbs.next(32)
            
if __name__ == "__main__":
    main()