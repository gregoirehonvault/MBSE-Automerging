PATH=$PATH:`pwd`/.gitconfig/

git branch exemple
git checkout exemple

git branch -D demo
git branch -D demo-branch-1
git branch -D demo-branch-2

git checkout -b demo
echo "in demo branch, try to add file with non-ASCII character"
cp ./exemple/¡.net ./¡.net
git add ¡.net
git commit -m "Wrong file name"
git rm --cached ¡.net

echo "in demo branch, create demo.xml"
cp ./exemple/demo.xml ./demo.xml
git add demo.xml
cp ./exemple/buffer.net ./buffer.net
git add buffer.net
git commit -m "demo: create demo.xml"

echo "create both demo-branch (1 and 2)"
git branch demo-branch-1
git branch demo-branch-2

echo "change demo.xml on demo-branch-1"
git checkout demo-branch-1
cp ./exemple/demo1.xml ./demo.xml
git add demo.xml
cp ./exemple/buffer1.net ./buffer.net
git add buffer.net
git commit -m "demo: change demo.xml - add class B"

echo "change demo.xml on demo-branch-2"
git checkout demo-branch-2
cp ./exemple/demo2.xml ./demo.xml
git add demo.xml
cp ./exemple/buffer2.net ./buffer.net
git add buffer.net
git commit -m "demo: change demo.xml - add class C"


echo "back to demo and try to merge all"
git checkout demo
echo "Merge demo-branch-1"
git merge demo-branch-1 -m "Merge 1"
echo "Merge demo-branch-2"
git merge demo-branch-2 -m "Merge 2"

