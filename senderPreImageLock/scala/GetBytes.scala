import scala.util.{Try, Success, Failure}
object GetBytes
{
  def main(args: Array[String])
  {
    if (args.length > 1)
    {
      println("too many args, enter one integer to get the byte format of")
      sys.exit
    }
    else if (args.length == 0)
    {
      print("enter the integer to get the byte format of")
      sys.exit
    }
    if (Try(args(0).toString).isSuccess)
    {
      var stringToBytes = args(0).toString.getBytes()
      var pyListBegin = "["
      var innerpyList = stringToBytes.mkString(",") //converting to pylist
      var result = pyListBegin.concat(innerpyList)
      var pyListEnd = "]"
      result = result.concat(pyListEnd)
      print(result)
    }
    else
    {
      print("argument", args(0), "is not a string")
      sys.exit
    }
  }
}

