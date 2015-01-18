package main

import (
	"math"
	"math/rand"
	"time"
	"fmt"
	"net/http"
	"github.com/russross/blackfriday"
	"strconv"
)

const (
	initialSquares int = 100
)

type Game struct {
	squares          [100]Square
	remainingSquares int
	AfcTeam          string
	NfcTeam          string
}

func (self Game) GetRemainingSquares() int {
	return self.remainingSquares
}

func (self Game) AddSquare(square Square) (success bool) {
	num := square.GetSquareNum()
	if self.squares[num].Name == nil {
		self.squares[num] = square
		self.remainingSquares--
		return true
	} else {
		return false
	}
}

func (self Game) UpdateSquare(square Square) {
	num := square.GetSquareNum()
	if self.squares[num].Name != nil && square.Name != nil {
		self.squares[num] = square
	} else if self.squares[num].Name != nil && square.Name == nil {
		self.squares[num] = square
		self.remainingSquares++
	} else if self.squares[num].Name == nil && square.Name != nil {
		self.squares[num] = square
		self.remainingSquares--
	}
}

func (self Game) RemoveSquare(pos int) {
	if self.squares[pos].Name != nil {
		self.squares[pos].Name = nil
		self.remainingSquares++
	}
}

type Square struct {
	NfcPos int
	AfcPos int
	Name   *string
}

func (self Square) GetSquareNum() int {
	return self.AfcPos*10 + self.NfcPos
}

func GetPositions(pos int) (afcPos, nfcPos int) {
	if pos < 0 || pos > initialSquares-1 {
		return -1, -1
	}
	if pos < 10 {
		return 0, pos
	}
	afcPos = int(math.Mod(float64(pos), 10))
	nfcPos = (pos - afcPos) / 10
	return
}

func GetRandomSquareNumbers() (afcNums, nfcNums []int) {
	rand.Seed(time.Now().UnixNano())
	afcNums = rand.Perm(10)
	nfcNums = rand.Perm(10)
	return
}

func NewGame() Game {
	game := new(Game)
	game.remainingSquares = initialSquares
	for i := 0; i < len(game.squares); i++ {
		afcPos, nfcPos := GetPositions(i)
		square := Square{NfcPos: nfcPos, AfcPos: afcPos}
		game.squares[i] = square
	}
	return *game
}

// TODO: Display current Super Bowl Squares status
func displaySquaresHandler(w http.ResponseWriter, r *http.Request) {
	mdStr := "# Super Bowl Squares\n\n||"

	afcNums, nfcNums := GetRandomSquareNumbers()

	for i := 0; i < len(afcNums); i++ {
		mdStr += strconv.Itoa(afcNums[i]) + "|"
	}
	mdStr += "\n|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|"
	for i := 0; i < len(nfcNums); i++ {
		mdStr += "\n|**" + strconv.Itoa(nfcNums[i]) + "**|"
		for j := 0; j < 10; j++ {
			temp := game.squares[i * 10 + j].Name
			if temp == nil {
				mdStr += "?|"
			} else {
				mdStr += *temp + "|"
			}
		}
	}
	mdBytes := []byte(mdStr)
	outputBytes := string(blackfriday.MarkdownCommon(mdBytes)[:])

	fmt.Fprintf(w, outputBytes)
}

var (
	game = NewGame()
)

func main() {
	test := "Test"
	game.squares[0].Name = &test
	http.HandleFunc("/", displaySquaresHandler)
	http.ListenAndServe(":8080", nil)
}
