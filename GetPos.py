L  =   780
Lu =   500
115 27
73  17

def main(y):
  ynew = (y*L - L + Lu)/Lu
  print ynew

  return ynew

if __name__ == '__main__':
  main(0.9)
  main(0.8)
  main(0.82)
