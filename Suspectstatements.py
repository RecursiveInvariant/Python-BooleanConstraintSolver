# SuspectStatements.py
# Author: Brendan McClurg
# Course: Discrete Mathematics
#
# Purpose:
# Determine the guilt or innocence of five suspects given that every
# guilty suspect lies and every innocent suspect tells the truth, then
# write the verdict(s) to a text file.
#
# Model:
# Each suspect is a Boolean guilt variable. Each statement is encoded
# as a logical expression over those variables. An assignment is valid
# when, for every enforced suspect, guilt is the opposite of that
# suspect's statement truth value (guilt XOR statement == true).
#
# Statements (hard-coded, one self-contained rule per suspect):
# Paul : R                Quinn: S -> R            Rob : S AND T
# Sid  : Q AND R          Todd : P OR R
#
# Parts:
# Part 1 - all five statements enforced -> one solution.
# Part 2 - Quinn omitted (four statements) -> list all solutions and
# report which suspects are definite or undetermined.
# Part 3 - accept an active list, e.g. "4 Paul Rob Sid Todd", from the
# command line or the input file; the same engine serves all.
#
# Input  : optional "count name ..." tokens (args, else input file);
# absent input defaults to all five suspects.
# Output : a labeled .txt file echoing the input, listing each solution
# in the required five-line format, with a summary.

# Standard library support for collections and text files.

# SuspectStatements solves the lying-suspects puzzle and writes verdicts
# to a text file, parameterized by which statements are enforced.
from __future__ import annotations
import sys
from enum import Enum, auto
from typing import TextIO


def _read_line(f):
    s = f.readline()
    return None if s == "" else s.rstrip("\r\n")


class OrderedSet(dict):
    # an insertion-ordered set: a dict whose values are ignored (LinkedHashSet)
    def add(self, x): self[x] = None
    def discard(self, x): self.pop(x, None)


DEFAULT_INPUT_FILE: str = "suspects_in.txt"
SUSPECT_ONE_NAME: str = "Paul"
SUSPECT_TWO_NAME: str = "Quinn"
SUSPECT_THREE_NAME: str = "Rob"
SUSPECT_FOUR_NAME: str = "Sid"
SUSPECT_FIVE_NAME: str = "Todd"
OUTPUT_FILE: str = "suspects_out.txt"

class Suspect(Enum):
    # Define stable identities and their corresponding display names.
    SUSPECT_ONE = SUSPECT_ONE_NAME
    SUSPECT_TWO = SUSPECT_TWO_NAME
    SUSPECT_THREE = SUSPECT_THREE_NAME
    SUSPECT_FOUR = SUSPECT_FOUR_NAME
    SUSPECT_FIVE = SUSPECT_FIVE_NAME

    # Store the display name associated with this suspect.
    _displayName: str

    # Construct a suspect with its assigned display name.
    # Inputs : displayName - the configured name for this suspect.
    def __init__(self, displayName: str):
        self._displayName = displayName
    # end Suspect()

    # Return the printable name associated with this suspect.
    # Output : the configured display name.
    def displayName(self) -> str:
        return self._displayName
    # end displayName()

    # Evaluate the statement associated with this suspect.
    # Inputs : g - the candidate guilt assignment.
    # Output : true when this suspect's statement is true.
    # Approach: select one statement rule using the stable identity.
    def holdsUnder(self, g: GuiltAssignment) -> bool:
        statementHolds: bool = False

        # Select the statement associated with this suspect's role.
        match self:
            # Suspect one: "Suspect three is guilty."
            # Original proposition: P states R.
            case Suspect.SUSPECT_ONE:
                statementHolds = g.isGuilty(Suspect.SUSPECT_THREE)
            # Suspect two: "If suspect four is guilty, then
            # suspect three is guilty."
            # Original proposition: Q states S -> R.
            case Suspect.SUSPECT_TWO:
                statementHolds = (not g.isGuilty(Suspect.SUSPECT_FOUR)) or g.isGuilty(Suspect.SUSPECT_THREE)
            # Suspect three: "Both suspect four and suspect
            # five are guilty."
            # Original proposition: R states S AND T.
            case Suspect.SUSPECT_THREE:
                statementHolds = g.isGuilty(Suspect.SUSPECT_FOUR) and g.isGuilty(Suspect.SUSPECT_FIVE)
            # Suspect four: "Both suspect two and suspect
            # three are guilty."
            # Original proposition: S states Q AND R.
            case Suspect.SUSPECT_FOUR:
                statementHolds = g.isGuilty(Suspect.SUSPECT_TWO) and g.isGuilty(Suspect.SUSPECT_THREE)
            # Suspect five: "At least one of suspect one
            # or suspect three is guilty."
            # Original proposition: T states P OR R.
            case Suspect.SUSPECT_FIVE:
                statementHolds = g.isGuilty(Suspect.SUSPECT_ONE) or g.isGuilty(Suspect.SUSPECT_THREE)
            # Reject an identity without an associated statement.
            case _:
                raise RuntimeError("Unknown suspect identity.")
        # end suspect statement by role

        return statementHolds
    # end holdsUnder()

class Status(Enum):
    DEFINITELY_GUILTY = auto()
    DEFINITELY_INNOCENT = auto()
    UNDETERMINED = auto()

class GuiltAssignment:
    # Guilt bitmask: bit i set means the suspect with ordinal i is guilty.
    guiltMask: int

    # Build an assignment directly from a guilt bitmask.
    # Inputs : guiltMask - the packed guilt bits. Output: none.
    def __init__(self, guiltMask: int):
        self.guiltMask = guiltMask
    # end GuiltAssignment()

    # Return true when the given suspect is guilty under this assignment.
    # Inputs : suspect. Output: the guilt Boolean for that suspect.
    def isGuilty(self, suspect: Suspect) -> bool:
        # Each suspect owns exactly one bit in the guilt mask.
        bit: int = 1 << list(type(suspect)).index(suspect)

        return (self.guiltMask & bit) != 0
    # end isGuilty()

class SuspectStatements:
    # Number of suspects, derived so the model scales if suspects change.
    SUSPECT_COUNT: int = len(list(Suspect))  # static

    # Total assignments to test: 2 raised to the suspect count.
    TOTAL_ASSIGNMENTS: int = 1 << SUSPECT_COUNT  # static

    # Fixed input file read when no command-line tokens are supplied.

    # Define the display names associated with each suspect role.
    # Names can change without changing the logical statement rules.

    # Fixed, human-readable text file that receives the solver output.

    # Entry point: resolve the active statement set, solve the puzzle,
    # and write the labeled solutions and summary to a named text file.
    # Inputs : args - optional "count name ..." specification tokens.
    # Output : none (produces the output text file and console status).
    @staticmethod
    def main():
        args: list[str] = sys.argv[1:]
        program: SuspectStatements = SuspectStatements()

        # 1. Resolve which suspects' statements to enforce.
        specTokens: list[str] = program.resolveSpecTokens(args)

        # Collect any input-rejection reasons so the output file can
        # record why the active set changed, not just the console.
        inputNotes: list[str] = []

        # 2. Build and validate the active set (defaults to all five).
        activeSet: OrderedSet = program.buildActiveSet(specTokens, inputNotes)

        # 3. Enumerate every assignment consistent with those statements.
        solutions: list[GuiltAssignment] = program.solve(activeSet)

        # 4. Persist echoed input, notes, solutions, and summary to disk.
        written: bool = program.writeResults(OUTPUT_FILE, activeSet, solutions, inputNotes)

        # 5. Report success only after the file has been written.
        if written:
            print(f"Done. Solutions written to {OUTPUT_FILE}")
    # end main()

    # Determine the raw specification tokens for the active statement set.
    # Inputs : args - command-line arguments (may be empty).
    # Output : token array; args win, else the input file's first
    # non-blank line, else an empty array (meaning "all five").
    # Approach: prefer args for script automation; fall back to a fixed
    # input file; a missing file yields an empty array.
    def resolveSpecTokens(self, args: list[str]) -> list[str]:
        tokens: list[str]

        # Prefer supplied command-line tokens over any file input.
        if len(args) > 0:
            tokens = args
        else:
            line: str = self.readSpecLine(DEFAULT_INPUT_FILE)

            # A missing or empty file activates the default full set.
            if line is None:
                tokens = []
            else:
                tokens = line.strip().split()

        return tokens
    # end resolveSpecTokens()

    # Read the first non-blank line from a named input file.
    # Inputs : fileName - the fixed input file path.
    # Output : the trimmed line, or null when the file is absent/empty.
    # Approach: guard I/O so a missing file becomes a clean null, not a
    # crash; this keeps the program script-friendly.
    def readSpecLine(self, fileName: str) -> str:
        result: str = None

        # Try-with-resources closes the reader automatically.
        try:
            with open(fileName) as reader:
                line: str = _read_line(reader)

                # Skip leading blank lines to the first real specification.
                while (line is not None) and len(line.strip()) == 0:
                    line = _read_line(reader)

                result = line
        except IOError as ioe:
            # Missing or unreadable file: treat as "no specification".
            result = None

        return result
    # end readSpecLine()

    # Build the validated set of suspects whose statements are enforced.
    # Inputs : tokens - "count name ..." (empty means use all five);
    # notes - list that receives any rejection reason for the
    # output file to echo.
    # Output : an ordered set of Suspect to constrain; never null.
    # Approach: empty -> all suspects. Otherwise the first token is an
    # expected count and the rest are names; validate the
    # count, resolve each name, reject duplicates, and fall
    # back to all five on any invalid input so the program
    # still produces legitimate output.
    def buildActiveSet(self, tokens: list[str], notes: list[str]) -> OrderedSet:
        # Preserve suspect order for stable, readable output.
        activeSet: OrderedSet = OrderedSet()
        valid: bool = True

        # Choose the complete set only when no specification was given.
        if len(tokens) == 0:
            # Default scenario: every suspect makes a statement.
            self.addAllSuspects(activeSet)
        else:
            expectedCount: int = self.parseCount(tokens[0])
            providedCount: int = len(tokens) - 1

            # The promised count must match the names that follow.
            if (expectedCount < 0) or (expectedCount != providedCount):
                self.reportInputError(f"Count {expectedCount} does not match the {providedCount} names provided.", notes)
                valid = False

            # Resolve names only while the input remains valid.
            index: int = 1
            while (index < len(tokens)) and valid:
                suspect: Suspect = self.findSuspect(tokens[index])

                # Reject unknown or repeated names before storing them.
                if suspect is None:
                    self.reportInputError(f"Unknown suspect name: {tokens[index]}.", notes)
                    valid = False
                elif suspect in activeSet:
                    self.reportInputError(f"Duplicate suspect name: {tokens[index]}.", notes)
                    valid = False
                else:
                    activeSet.add(suspect)
                index += 1

        # Any invalid input falls back to the full set of suspects.
        if not valid:
            activeSet.clear()
            self.addAllSuspects(activeSet)

        return activeSet
    # end buildActiveSet()

    # Parse the leading count token into a non-negative integer.
    # Inputs : token - the first specification token.
    # Output : the parsed count, or -1 when the token is not an integer.
    def parseCount(self, token: str) -> int:
        count: int

        # Guard the parse so malformed input cannot crash the program.
        try:
            count = int(token)
        except ValueError as nfe:
            count = -1

        return count
    # end parseCount()

    # Add every suspect, in declaration order, to the target set.
    # Inputs : target - the set to populate. Output: none (mutates it).
    def addAllSuspects(self, target: set[Suspect]):
        # Add each defined suspect to the active statement set.
        for suspect in Suspect:
            target.add(suspect)
    # end addAllSuspects()

    # Return the suspect whose name matches, or null when none match.
    # Inputs : name - a candidate name (any case).
    # Output : the matching Suspect, or null. Approach: case-insensitive
    # linear scan over the five constants.
    def findSuspect(self, name: str) -> Suspect:
        match: Suspect = None

        # Compare the requested name against each defined suspect.
        for suspect in Suspect:
            # Match each candidate against the requested suspect name.
            if suspect._displayName.lower() == name.lower():
                match = suspect

        return match
    # end findSuspect()

    # Report an input problem to the console and record it for the file.
    # Inputs : message - the human-readable reason; notes - the list the
    # output file will echo. Output: none (prints to the console
    # and appends one self-contained note).
    def reportInputError(self, message: str, notes: list[str]):
        # Console evidence for an interactive or scripted run.
        print(f"Input error: {message}", file=sys.stderr)
        print("Falling back to all five statements.", file=sys.stderr)

        # File evidence: one line the output can print verbatim.
        notes.append(f"{message} Defaulted to all five statements.")
    # end reportInputError()

    # Collect every guilt assignment consistent with the active set.
    # Inputs : activeSet - suspects whose truth constraints must hold.
    # Output : the list of valid assignments (0, 1, or many).
    # Approach: exhaustively enumerate all 2^n assignments as bitmasks
    # and keep those that satisfy every active constraint.
    def solve(self, activeSet: set[Suspect]) -> list[GuiltAssignment]:
        solutions: list[GuiltAssignment] = []

        # Examine every possible five-suspect guilt assignment once.
        for mask in range(SuspectStatements.TOTAL_ASSIGNMENTS):
            candidate: GuiltAssignment = GuiltAssignment(mask)

            # Retain only assignments satisfying every active statement.
            if self.isValidAssignment(candidate, activeSet):
                solutions.append(candidate)

        return solutions
    # end solve()

    # Test one assignment against every active suspect's constraint.
    # Inputs : g - the candidate assignment; activeSet - enforced set.
    # Output : true when every guilty suspect lies and every innocent
    # one tells the truth; false otherwise.
    # Approach: a suspect is consistent when guilt XOR statement is true,
    # so the assignment fails once guilt equals statement.
    def isValidAssignment(self, g: GuiltAssignment, activeSet: set[Suspect]) -> bool:
        valid: bool = True

        # Only active statements constrain the candidate assignment.
        for suspect in activeSet:
            statementHolds: bool = suspect.holdsUnder(g)
            guilty: bool = g.isGuilty(suspect)

            # Guilt must be the opposite of the statement's truth value.
            if guilty == statementHolds:
                valid = False

        return valid
    # end isValidAssignment()

    # Classify each suspect across all valid solutions (used for Part 2).
    # Inputs : solutions - every valid assignment found.
    # Output : a map from suspect to its determination status.
    # Approach: a suspect is definite only when guilty in all solutions
    # or innocent in all; a mix is undetermined, and an empty
    # solution list leaves every suspect undetermined.
    def classifySuspects(self, solutions: list[GuiltAssignment]) -> dict[Suspect, Status]:
        verdicts: dict[Suspect, Status] = {}

        # Classify each suspect independently across the solution set.
        for suspect in Suspect:
            guiltyCount: int = self.countGuilty(suspect, solutions)
            status: Status = self.statusFor(guiltyCount, len(solutions))

            verdicts[suspect] = status

        return verdicts
    # end classifySuspects()

    # Count how many solutions mark the given suspect guilty.
    # Inputs : suspect; solutions. Output: the guilty tally.
    def countGuilty(self, suspect: Suspect, solutions: list[GuiltAssignment]) -> int:
        guiltyCount: int = 0

        # Count each assignment in which this suspect is guilty.
        for g in solutions:
            # Add only solutions that mark this suspect guilty.
            if g.isGuilty(suspect):
                guiltyCount = guiltyCount + 1

        return guiltyCount
    # end countGuilty()

    # Map a guilty tally to a determination status.
    # Inputs : guiltyCount; total - number of solutions.
    # Output : the Status for the suspect. Approach: all-guilty or
    # all-innocent is definite; anything else is undetermined.
    def statusFor(self, guiltyCount: int, total: int) -> Status:
        status: Status

        # An empty solution set cannot establish any individual verdict.
        if total == 0:
            status = Status.UNDETERMINED
        elif guiltyCount == total:
            status = Status.DEFINITELY_GUILTY
        elif guiltyCount == 0:
            status = Status.DEFINITELY_INNOCENT
        else:
            status = Status.UNDETERMINED

        return status
    # end statusFor()

    # Build the required verdict line for one suspect under an assignment.
    # Inputs : suspect; g - the assignment. Output: "Paul is guilty." etc.
    def formatVerdict(self, suspect: Suspect, g: GuiltAssignment) -> str:
        verdict: str

        # Produce one verdict line for the chosen guilt configuration.
        if g.isGuilty(suspect):
            verdict = f"{suspect.displayName()} is guilty."
        else:
            verdict = f"{suspect.displayName()} is innocent."

        return verdict
    # end formatVerdict()

    # Write echoed input, all solutions, and a summary to a text file.
    # Inputs : outFile; activeSet - enforced suspects; solutions;
    # notes - any input-rejection reasons to record.
    # Output : true if file writing succeeded; false on I/O error.
    # Approach: record any rejection reason, echo the active set, print
    # each solution as five verdict lines in fixed order
    # separated by blank lines, then a count; when several
    # solutions exist append the Part 2 breakdown. All I/O is
    # guarded so failures are reported.
    def writeResults(self, outFile: str, activeSet: set[Suspect], solutions: list[GuiltAssignment], notes: list[str]) -> bool:
        successful: bool = False

        # Try-with-resources flushes and closes the writer automatically.
        try:
            with open(outFile, "w") as writer:
                print("Suspect Statements - Solver Output", file=writer)
                print("----------------------------------", file=writer)

                # Record any input-rejection reason in the file itself, so a
                # changed active set is explained without a console log.
                self.writeInputNotes(writer, notes)

                # Echo the input so the run is self-documenting.
                print(f"Statements used: {self.describeActiveSet(activeSet)}", file=writer)

                print(f"Valid solutions found: {len(solutions)}", file=writer)
                print(file=writer)

                # Emit each solution in the required five-line format.
                solutionNumber: int = 1

                # Write a separate five-line verdict for each valid solution.
                for g in solutions:
                    print(f"Solution {solutionNumber}:", file=writer)

                    # Print every suspect in the fixed declaration order.
                    for suspect in Suspect:
                        print(self.formatVerdict(suspect, g), file=writer)

                    print(file=writer)
                    solutionNumber = solutionNumber + 1

                # Multiple assignments require a cross-solution determination.
                if len(solutions) > 1:
                    self.writeClassification(writer, solutions)

                # PrintWriter records errors; check them explicitly.
                writer.flush()
                successful = True

                # Report a writing failure instead of claiming completion.
                if not successful:
                    print(f"I/O error writing {outFile}.", file=sys.stderr)
        except IOError as ioe:
            print(f"I/O error writing {outFile}: {str(ioe)}", file=sys.stderr)

        return successful
    # end writeResults()

    # Render the active set as a readable, comma-separated name list.
    # Inputs : activeSet. Output: e.g. "Paul, Rob, Sid, Todd".
    def describeActiveSet(self, activeSet: set[Suspect]) -> str:
        builder: str = ""

        # Append each active name, separating successive names by commas.
        for suspect in activeSet:
            # Separate names after the first with a comma and a space.
            if len(builder) > 0:
                builder += ", "

            builder += str(suspect.displayName())

        return str(builder)
    # end describeActiveSet()

    # Write any input-rejection notes to the output file.
    # Inputs : writer - open output writer; notes - recorded reasons.
    # Output : none. Approach: print a labeled block only when at least
    # one reason exists, so clean runs stay uncluttered.
    def writeInputNotes(self, writer: TextIO, notes: list[str]):
        # Print the block only when a reason was recorded.
        if len(notes) != 0:
            print("Input notes:", file=writer)

            # Print each recorded reason on its own indented line.
            for note in notes:
                print(f"    {note}", file=writer)

            print(file=writer)
    # end writeInputNotes()

    # Append the definite / undetermined breakdown to the output file.
    # Inputs : writer - open output writer; solutions - all results.
    # Output : none (writes to the provided writer).
    def writeClassification(self, writer: TextIO, solutions: list[GuiltAssignment]):
        verdicts: dict[Suspect, Status] = self.classifySuspects(solutions)

        print("Determination across all valid solutions:", file=writer)

        # Write one cross-solution determination for each suspect.
        for suspect in Suspect:
            status: Status = verdicts[suspect]

            print(f"    {suspect.displayName()}: {self.describeStatus(status)}", file=writer)
    # end writeClassification()

    # Convert a Status into human-readable text for the output file.
    # Inputs : status. Output: the display phrase for that status.
    def describeStatus(self, status: Status) -> str:
        text: str

        # Map each determination to plain language for the reader.
        match status:
            case Status.DEFINITELY_GUILTY:
                text = "definitely guilty"
            case Status.DEFINITELY_INNOCENT:
                text = "definitely innocent"
            case _:
                text = "undetermined"

        return text
    # end describeStatus()

    # Suspect enumerates the five logical identities and associates each
    # identity with its configurable display name and statement rule.
    # end enum Suspect

    # Status enumerates the determination categories for a suspect across
    # all valid solutions.
    # end enum Status

    # GuiltAssignment represents one guilt configuration for all suspects as
    # a bitmask, where bit i corresponds to the suspect with ordinal i.
    # end class GuiltAssignment
# end class SuspectStatements


if __name__ == "__main__":
    SuspectStatements.main()