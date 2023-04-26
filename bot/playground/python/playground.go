package main

import (
	"fmt"
	"io"
	"os"
	"os/exec"
	"strings"
	"syscall"
	"time"
)

const (
	maxExecutionTime = 5 // 5 seconds
)

func main() {
	if len(os.Args) != 4 {
		fmt.Println("Usage: ./playground <filename> <input> <result>")
		os.Exit(1)
	}

	f, err := os.Open(os.Args[1])
	if err != nil {
		fmt.Println("Error opening file:", err)
		os.Exit(1)
	}
	defer f.Close()

	fileInfo, err := f.Stat()
	if err != nil {
		fmt.Println("Error getting file info:", err)
		os.Exit(1)
	}

	fileContents := make([]byte, fileInfo.Size())
	_, err = f.Read(fileContents)
	if err != nil {
		fmt.Println("Error reading file:", err)
		os.Exit(1)
	}

	cmd := exec.Command("python", os.Args[1])
	stdin, err := cmd.StdinPipe()
	if err != nil {
		fmt.Println(err)
	}
	var outbuf, errbuf strings.Builder
	cmd.Stdout = &outbuf
	cmd.Stderr = &errbuf

	io.WriteString(stdin, os.Args[2])
	stdin.Close()

	err = cmd.Start()
	if err != nil {
		fmt.Println(err)
	}
	timeout := time.After(time.Duration(maxExecutionTime) * time.Second)
	done := make(chan error, 1)
	go func() {
		done <- cmd.Wait()
	}()
	select {
	case <-timeout:
		if err := cmd.Process.Kill(); err != nil {
			fmt.Println("Error killing process:", err)
			os.Exit(0)
		}
		fmt.Println("Execution timed out")
		os.Exit(0)
	case err := <-done:
		if err != nil {
			fmt.Println("Error running command:", err)
			os.Exit(1)
		}
	}

	exitCode := 0
	if exitError, ok := cmd.ProcessState.Sys().(syscall.WaitStatus); ok {
		exitCode = exitError.ExitStatus()
	}

	stdout := outbuf.String()
	fmt.Println(strings.EqualFold(string(stdout[:len(stdout)-1]), os.Args[3]))
	os.Exit(exitCode)
}
