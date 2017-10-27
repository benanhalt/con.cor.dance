Title: Migrating the Specify 6 Subversion Repository to Git
Date: Fri Oct 27 12:14:00 CDT 2017
Category: programming
Tags: svn, git, github
Status: draft

Until now the Specify 6 source code has been version controlled using
Subversion. The decision was made to migrate the repository to
Git. Here are some notes on how this was accomplished.

## git-svn

The rough draft of the migration was obtained using the *git-svn*
tool. One can find plenty of material about its use, so I will just
describe the particular choices I made as a sort of case study.

### authors.txt

Since SVN commits are labeled by SVN usernames while Git uses email
addresses, *git-svn* accepts a mapping file that it uses to determine
the author of the commits as they are replayed into the Git
repository. The SVN usernames are easily obtained from the log.

```
svn log -q \
   | grep -e '^r' \
   | awk 'BEGIN { FS = "|" }; { print $2 }' \
   | sort -u \
   > authors.txt
```

The resulting `authors.txt` file is then filled in with the
corresponding email addresses.

I think this is worth doing, particularly if the result repository is
going into GitHub, so that contributors will be correctly
attributed. An interesting aspect of this process is determining the
identities of past contributors given only the SVN user. My approach
was searching the project mailing list archives, since it also contains a
record of these contributors along with their real names and email
addresses.

### Branches and Tags

It is possible to point *git-svn* to the tags and branches directories
of an SVN repository and have it try to recapitulate the branch and
merge history in Git. I made an initial attempt at using this
capability, but it didn't seem to work on the first try. I decided
that since we haven't been using SVN branches for the past few years,
I wouldn't bother with trying to preserve them. From a preservation
perspective it makes more sense to archive the SVN repository
as a primary source rather than worrying about producing exact
fidelity in a derivative artifact that's primary use is day-to-day
development work.

With the completed `authors.txt` file in hand, a simple migration of
the SVN trunk into Git is straightforward.

```
git-svn clone --prefix=svn/ --trunk=trunk/Specify \
   --authors-file=authors.txt \
   https://svn.code.sf.net/p/specify/code \
   specify2git
```

I don't remember exactly how long it took for *git-svn* to replay the
roughly 12,000 commits into the new Git repository. Perhaps an
hour. Too long to sit and watch, but not agonizingly slow either.

### Rewriting History

The resulting Git repository was approximately 600MB. A lot of the
bulk comes from the project dependencies that are included in the
repository as JAR files. This is not an ideal situation, but it is
what it is. I briefly investigated some sort of *git-annex* solution
to separate the libraries, but decided to take things one step at a
time.

Still, in the interest of curiosity I wanted to see what were the
worst offenders in terms of file size. Perhaps I would learn something
that would produce an easy win in reducing the size. Some Googling led
me to the following method for finding the largest objects in the Git
repository adapted from
this [StackOverflow answer](https://stackoverflow.com/a/42544963).

```
git rev-list --objects --all \
   | git cat-file \
      --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
   | grep '^blob' \
   | sort --numeric-sort --key=3 
```

Sure enough, the largest object was an SQL file of some test data that
had been removed at some point in the past. It was over 170MB. I was
pretty sure it could be safely removed from the project history, but I
wanted to see why it was there and when it had gone away. You can see
the history of deleted files using *git log*, but you have to say `git
log -- path/to/deleted/file`, or Git will think the file path is the
name of a branch or something.

In this case, there were only two commits that touched the file. The
one that added it and the immediate successor with the message
"Accidently checked in"! No doubt I could remove this file from the
history and immediately reduce the size of the repository by nearly
30%.

I've used `git rebase` before to rewrite history, but I knew there
were better options for these kind of bulk operations. Some research
turned up an excellent post from Manish
Goregaokar,
[Understanding Git filter-branch and the Git Storage Model](https://manishearth.github.io/blog/2017/03/05/understanding-git-filter-branch/). I
was quickly able to figure out how to excise the file.

```
git filter-branch -f --prune-empty --index-filter \
   'git rm --cached --ignore-unmatch path/to/file' HEAD
```

The operation took about five minutes to complete. 

Emboldened by this success, I returned to the list of large files in
search of more targets. I was able to eliminate a few large demo
files. I also found instances where whole subdirectories had been
accidentally committed. In one, someone had committed the actual
installation directory into the repository including an embedded
MySQL database! In another, the entire source code repository had been
added as a subdirectory of itself. This didn't add much to the size
since Git only stores a single copy of identical files, but I blew it
away just the same.

Some of these accidental commits also included changes besides new
files that were also later reverted by a subsequent commit. I
removed these pairs of commits using `git rebase -i` on branches I
created pointing to the reverting commit. I then used `git rebase
--onto` to rewrite the later history onto those branches.

If I ever do something like this again, I should remember to search
the commit logs for "accident*" and similar messages.

### The Results

After all of this, the Git repository ended up being about 350MB
according to `du -h .git/objects/`. Because Git retains old references
when using *filter-branch* and *rebase*, the size reduction is not
immediately apparent, even after `git gc`. The easiest way to get an
accurate measurement is to make a new clone of the repository using
`git clone file://path/to/cleaned/up/repository new-clone`. Only the
objects actually reachable from *HEAD* will be brought over, but it is
necessary to use the `file://` style URI. Cloning the directory
directly only creates hardlinks.
