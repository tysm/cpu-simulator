#!/usr/bin/env python

"""
assembler.py: rather primitive two-pass assembler. Get the labels, then
assemble the instructions.
"""

import re
import sys
import optparse

symbols = {}

instructions = []

relocations = []

class AssemblerError(Exception):
  pass

class AssemblerSyntaxError(AssemblerError):
  def __init__(self,line,reason):
    self.line = line
    self.reason = reason
  def __str__(self):
    return "Syntax error on line %d: %s" % (self.line,self.reason)

class AssemblerRangeError(AssemblerError):
  def __init__(self,line,reason):
    self.line = line
    self.reason = reason
  def __str__(self):
    return "Range error on line %d: %s" % (self.line,self.reason)

labelre = re.compile(r"""^(?P<labels>.*:)?(?P<gunk>[^:]*)$""")
commentre = re.compile(r"""^(?P<important>[^#]*)(?P<comment>#.*)?$""")
alnumunderre = re.compile(r"""^\w+$""")

#or and add sub slt sltu addu subu
rtype_re  = re.compile(r'''^(?P<instr>(or|and|add|mult|slt|sll|srl|xor))\s+(?P<rd>\$(0|zero|v0|s[0-2]|a0|sp|ra))\s+(?P<rs>\$(0|zero|v0|s[0-2]|a0|sp|ra))\s+(?P<rt>\$(0|zero|v0|s[0-2]|a0|sp|ra))$''')
#multu divu
mult_re    = re.compile(r'''^(?P<instr>(mult))\s+(?P<rs>\$(0|zero|v0|s[0-2]|a0|sp|ra))\s+(?P<rt>\$(0|zero|v0|s[0-2]|a0|sp|ra))$''')
#mfhi mflo
mf_re    = re.compile(r'''^(?P<instr>(mfhi|mflo))\s+(?P<rd>\$(0|zero|v0|s[0-2]|a0|sp|ra))$''')
#sll srl sra
shift_re  = re.compile(r'''^(?P<instr>(sll|srl|sra))\s+(?P<rd>\$(0|zero|at|v[0,1]|a[0-3]|t[0-9]|s[0-7]|k[0-1]|gp|fp|sp|ra))\s+(?P<rt>\$(0|zero|at|v[0,1]|a[0-3]|t[0-9]|s[0-7]|k[0-1]|gp|fp|sp|ra))\s+(?P<immed>-?(0x)?[0-9a-fA-F]+)$''')
#ori addi addiu andi
immed_re  = re.compile(r'''^(?P<instr>(ori|addi|andi|slti|jr))\s+(?P<rt>\$(0|zero|v0|s[0-2]|a0|sp|ra))\s+(?P<rs>\$(0|zero|v0|s[0-2]|a0|sp|ra))\s+(?P<immed>-?(0x)?[0-9a-fA-F]+)$''')
#lui
lui_re    = re.compile(r'''^(?P<instr>lui)\s+(?P<immed>-?(0x)?[0-9a-fA-F]+)$''')
#sw lw sb lb lbu sh lhu swinc
mem_re    = re.compile(r'''^(?P<instr>(lb|sb|lh|sh))\s+(?P<rt>\$(0|zero|v0|s[0-2]|a0|sp|ra))\s+(?P<immed>-?(0x)?[0-9a-fA-F]+)\s*\(\s*(?P<rs>\$(0|zero|v0|s[0-2]|a0|sp|ra))\s*\)$''')
#j jal
j_re      = re.compile(r'''^(?P<instr>(j))\s+(?P<rd>\$(0|zero|v0|s[0-2]|a0|sp|ra))\s+(?P<label>\w+)$''')
#beq bne
branch_re = re.compile(r'''^(?P<instr>(beq|bne))\s+(?P<rs>\$(0|zero|v0|s[0-2]|a0|sp|ra))\s+(?P<rt>\$(0|zero|v0|s[0-2]|a0|sp|ra))\s+(?P<label>\w+)$''') #note switch
#jr
jr_re     = re.compile(r'''^(?P<instr>(jr))\s+(?P<rt>\$(0|zero|v0|s[0-2]|a0|sp|ra))\s+(?P<rs>\$(0|zero|v0|s[0-2]|a0|sp|ra))\s+(?P<immed>-?(0x)?[0-9a-fA-F]+)$''')
#la
la_re     = re.compile(r'''^(?P<instr>(la))\s+(?P<rt>\$(0|zero|v0|s[0-2]|a0|sp|ra))\s+(?P<label>\w+)$''')
signed_re = re.compile(r'addi|beq|bne|lh|sh|sb|lb|slti|jr')
both_allowed_re = re.compile(r'ori|andi')

opcodes = {
  'lui':0x1,
  'j':0x2,
  'jr':0x3,
  'beq':0x4,
  'bne':0x5,
  'addi':0x6,
  'slti':0x7,
  'andi':0x8,
  'ori':0x9,
#  'lb':0xa,
  'lh':0xa,
#  'sb':0xc,
  'sh':0xb,
  'mfhi':0xc,
  'mflo':0xd
}

functs = {
  'sll':0x0,
  'srl':0x1,
  'add':0x2,
  'and':0x3,
  'or':0x4,
  'xor':0x5,
  'slt':0x6,
  'mult': 0x7,
}

registers = {
  '0':0,
  'zero':0,
  'ra':1,
  's0':2,
  's1':3,
  's2':4,
  'a0':5,
  'v0':6,
  'sp':7,
}
def isPseudoInstruction(s):
  return la_re.match(s) or li_re.match(s)

def validLabel(s):
  return alnumunderre.match(s) != None

def fill_symbol_table(inputFile):
  lineNo = 1
  instructionsSeen = 0
  for line in inputFile:
    #strip any comments
    match = commentre.match(line)
    
    if not match:
      raise AssemblerSyntaxError(lineNo,"Unable to parse line: %s" % line)
    
    line = match.group('important')
    
    line = line.strip()
    
    match = labelre.match(line)
    
    if not match:
      raise AssemblerSyntaxError(lineNo,"Unable to parse line: %s" % line)
    
    labels_string = match.group('labels')
    
    if labels_string:
      labels = labels_string[:-1].split(':')
    else:
      labels = []
    
    for label in labels:
      if not validLabel(label):
        raise AssemblerSyntaxError(lineNo,"Invalid label: '%s'"%label)
      if label in symbols:
        raise AssemblerSyntaxError(lineNo,"Label %s already defined" % label)
      symbols[label] = instructionsSeen
    
    instruction = match.group('gunk').replace(',',' ').strip()
    if len(instruction) != 0:
      #there's an instruction here, so increment the number of instructions
      #if we had any pseudoinstructions, we'd do analysis and increment by
      #more than one here
      instructionsSeen += 1
    lineNo+=1

def imm_check(signed,both_allowed,immediate,lineNo):
  if both_allowed:
    if (immediate > 2 ** 6 - 1 or immediate < -(2 ** 6)):
        raise AssemblerSyntaxError(lineNo,"immediate out of range")
  else:
    if signed and (immediate > 2 ** 6 - 1 or immediate < -(2 ** 6)):
        raise AssemblerSyntaxError(lineNo,"signed immediate out of range")
    if (not signed) and (immediate > 2 ** 6 - 1 or immediate < 0):
        raise AssemblerSyntaxError(lineNo,"unsigned immediate out of range")
def lui_imm_check(immediate,lineNo):
  if (immediate > 2 ** 10 - 1 or immediate < -(2 ** 10)):
        raise AssemblerSyntaxError(lineNo,"immediate out of range")

def shamt_check(shamt,lineNo):
  if(shamt > 31 or shamt < 0):
    raise AssemblerSyntaxError(lineNo,"shamt out of range")


def assemble_instructions(inputFile):
  lineNo = 1
  instructionsSeen = 0
  instructions = []
  for line in inputFile:
    #strip any comments
    match = commentre.match(line)
    assert(match)
    line = match.group('important')
    
    line = line.strip()
    
    match = labelre.match(line)
    
    instruction = match.group('gunk').replace(',',' ').strip()

    rtype    = rtype_re.match(instruction)
    mult     = mult_re.match(instruction)
    move     = mf_re.match(instruction)
#    shift    = shift_re.match(instruction)
    shift = False
    immed    = immed_re.match(instruction)
    lui      = lui_re.match(instruction)
    mem      = mem_re.match(instruction)
    j        = j_re.match(instruction)
    branch   = branch_re.match(instruction)
#    jr       = jr_re.match(instruction)
    jr = False
    signed   = signed_re.match(instruction)
    both_allowed = both_allowed_re.match(instruction)
     
    if len(instruction) != 0:
      num = 0
      if rtype:
        rs = registers[rtype.group('rs')[1:]]
        rt = registers[rtype.group('rt')[1:]]
        rd = registers[rtype.group('rd')[1:]]
        funct = functs[rtype.group('instr')]
        num = 0 << 12 | rd << 9 | rs << 6 | rt << 3 | funct
        debug("instruction: %s rtype: rd: %d rs: %d rt: %d funct:%d num: %04x" % (instruction,rd,rs,rt,funct,num))
      elif mult:
        rs = registers[mult.group('rs')[1:]]
        rt = registers[mult.group('rt')[1:]]
        funct = functs[mult.group('instr')]
        num = 0 << 12 | 0 << 9 | rs << 6 | rt << 3 | funct
        debug("instruction: %s rs: %d rt: %d funct:%d num: %04x" % (instruction,rs,rt,funct,num))
      elif move:
        rd = registers[move.group('rd')[1:]]
        opcode = opcodes[move.group('instr')]
        num = opcode << 12 | rd << 9 | 0 << 6
        debug("instruction: %s rd: %d opcode:%d num: %04x" % (instruction,rd,opcode,num))

      elif shift:
        rt = registers[shift.group('rt')[1:]]
        rd = registers[shift.group('rd')[1:]]
        immediate = int(shift.group('immed'),0)
        funct = functs[shift.group('instr')]
        shamt_check(immediate,lineNo)
        num = 0 << 26 | 0 << 21 | rt << 16 | rd << 11 | (immediate & 31) << 6 | funct
        debug("instruction: %s rtype: rs: %d rd: %d shamt: %d funct:%d num: %04x" % (instruction,rt,rd,immediate,funct,num))
      elif immed:
        rs = registers[immed.group('rs')[1:]]
        rt = registers[immed.group('rt')[1:]]
        opcode = opcodes[immed.group('instr')]
        immediate = int(immed.group('immed'),0)
        imm_check(signed,both_allowed,immediate,lineNo)
        num = opcode << 12 | rt << 9 | rs << 6 | (immediate & 0b111111)
        debug("instruction: %s rd: %d rs: %d opcode: %d immediate: %d num: %04x" % (instruction,rt,rs,opcode,immediate,num))
      elif lui:
        # rt = registers[lui.group('rt')[1:]]
        opcode = opcodes[lui.group('instr')]
        immediate = int(lui.group('immed'),0)
        lui_imm_check(immediate,lineNo)
        num = opcode << 12 | 0 << 10 | (immediate & 0b1111111111)
        debug("instruction: %s opcode: %d immediate: %d num: %04x" % (instruction,opcode,immediate,num))
      elif mem:
        opcode = opcodes[mem.group('instr')]
        rs = registers[mem.group('rs')[1:]]
        rt = registers[mem.group('rt')[1:]]
        immediate = int(mem.group('immed'),0)
        imm_check(signed,both_allowed,immediate,lineNo)
        num = opcode << 12 | rt << 9 | rs << 6 | (immediate & 0b111111)
        debug("instruction: %s rd: %d rs: %d opcode: %d immediate: %d num: %04x" % (instruction,rt,rs,opcode,immediate,num))
      elif j:
        rd = registers[j.group('rd')[1:]]
        if rd > 3:
          raise AssemblerRangeError(lineNo, "Cannot use %s as link register" % mem.group('rd'))
        opcode = opcodes[j.group('instr')]
        #find label
        label = j.group('label')
        if label not in symbols:
          raise AssemblerSyntaxError(lineNo,"unknown label %s" % j.group('label'))
        instructionNo = symbols[label]
        thisInstruction = instructionsSeen
        if thisInstruction & 0xF800 != instructionNo & 0xF800:
          raise AssemblerRangeError(lineNo,"label %s is in another jump zone (instr: %04x, target:%04x)" % (label,thisInstruction,instructionNo))
        instructionNo *= 2
        num = opcode << 12 | rd << 10 | (instructionNo & 0x3FF)
        debug("instruction: %s addr: %d num: %04x" % (instruction,instructionNo & 0x3FF,num))
      elif branch:
        rs = registers[branch.group('rs')[1:]]
        rt = registers[branch.group('rt')[1:]]
        opcode = opcodes[branch.group('instr')]
        #find label
        label = branch.group('label')
        if label not in symbols:
          raise AssemblerSyntaxError(lineNo,"unknown label %s" % branch.group('label'))
        instructionNo = symbols[label]
        offset = instructionNo - (instructionsSeen)
        if offset > 2 ** 6 - 1 or offset < -(2 ** 6):
          raise AssemblerRangeError(lineNo,"label %s is too far away: %d instructions from pc" % (label,offset))
        offset *= 2
        num = opcode << 12 | rt << 9 | rs << 6 | (offset & 0b111111)
        debug("instruction: %s rs: %d rd: %d opcode: %d offset: %d num: %04x" % (instruction,rs,rt,opcode,offset,num))
      elif jr:
        rs = registers[jr.group('rs')[1:]]
        rt = registers[jr.group('rt')[1:]]
        opcode = opcodes[jr.group('instr')]
        immediate = int(immed.group('immed'),0)
        imm_check(signed,both_allowed,immediate,lineNo)
        num = opcode << 12 | rt << 9 | rs << 6 | (immediate & 0b111111)
        debug("instruction: %s rd: %d rs: %d opcode: %d immediate: %d num: %04x" % (instruction,rt,rs,opcode,immediate,num))
      else:
        raise AssemblerSyntaxError(lineNo,"Can't parse instruction '%s'" % instruction)
      #there's an instruction here, so increment the number of instructions
      #if we had any pseudoinstructions, we'd do analysis and increment by
      #more than one here
      instructionsSeen += 1
      instructions.append(num)
    lineNo+=1
  return instructions

def print_instructions(instructions,outfile):
  print >> outfile, "v2.0 raw"
  for instruction in instructions:
    print >> outfile, "%04x" % instruction

verbose = False

def debug(*args):
  if verbose:
    sys.stdout.write(' '.join([str(arg) for arg in args]) + '\n')

if __name__ == "__main__":
  usage = "%prog infile [options]"
  parser = optparse.OptionParser(usage=usage)
  parser.add_option('-o','--out',dest='output_file',type='string',
                    default='a.hex',help="Specify output filename")
  parser.add_option('-v','--verbose',dest='verbose',
                    action='store_true',default=False, help='verbose debug mode')
  options,args = parser.parse_args()
  if len(args) != 1:
    parser.error("Incorrect command line arguments")
    sys.exit(1)
  
  verbose = options.verbose
  
  output_file = options.output_file
  input_file = args[0]
  if re.match(r""".*(?P<extension>\.s)$""",input_file,re.I) and output_file == 'a.hex':
    output_file = input_file[:-1] + "hex"
  
  try:
    infile = open(input_file)
  except IOError,e:
    print >> sys.stderr, "Unable to open input file %s" % input_file
    sys.exit(1)
  try:
    fill_symbol_table(infile)
    infile.seek(0)
    instructions = assemble_instructions(infile)
    infile.close()
  except AssemblerError, e:
    print >> sys.stderr, str(e)
    sys.exit(1)
  try:
    outfile = open(output_file,'w')
    print_instructions(instructions,outfile)
    outfile.close()
  except IOError,e:
    print >> sys.stderr, "Unable to write to output file %s" % output_file
    sys.exit(1)
  sys.exit(0)
