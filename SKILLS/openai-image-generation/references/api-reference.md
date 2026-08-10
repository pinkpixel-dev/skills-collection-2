# OpenAI Image Generation — Full API Reference

Complete code examples for GPT Image models (`gpt-image-2` and prior) across the **Image API** and **Responses API**. See `SKILL.md` for the model list, pricing tables, and output customization options.

## Table of contents
1. [Generate images — Image API](#1-generate-images--image-api)
2. [Generate images — Responses API](#2-generate-images--responses-api)
3. [Multi-turn image generation](#3-multi-turn-image-generation)
4. [Streaming](#4-streaming)
5. [Revised prompt](#5-revised-prompt)
6. [Edit images — reference images](#6-edit-images--reference-images-responses-api)
7. [Edit images — reference images (Image API)](#7-edit-images--reference-images-image-api)
8. [Edit images with a mask](#8-edit-images-with-a-mask)
9. [Mask requirements & adding an alpha channel](#9-mask-requirements--adding-an-alpha-channel)
10. [Image input fidelity](#10-image-input-fidelity)
11. [Handling blocked requests and errors](#11-handling-blocked-requests-and-errors)

---

## 1. Generate images — Image API

```javascript
import OpenAI from "openai";
import fs from "fs";
const openai = new OpenAI();

const prompt = `
A children's book drawing of a veterinarian using a stethoscope to
listen to the heartbeat of a baby otter.
`;

const result = await openai.images.generate({
  model: "gpt-image-2",
  prompt,
});

// Save the image to a file
const image_base64 = result.data[0].b64_json;
const image_bytes = Buffer.from(image_base64, "base64");
fs.writeFileSync("otter.png", image_bytes);
```

```python
from openai import OpenAI
import base64

client = OpenAI()

prompt = """
A children's book drawing of a veterinarian using a stethoscope to
listen to the heartbeat of a baby otter.
"""

result = client.images.generate(model="gpt-image-2", prompt=prompt)

image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

# Save the image to a file
with open("otter.png", "wb") as f:
    f.write(image_bytes)
```

```go
package main

import (
	"context"
	"encoding/base64"
	"os"

	"github.com/openai/openai-go/v3"
)

func main() {
	client := openai.NewClient()
	result, err := client.Images.Generate(context.Background(), openai.ImageGenerateParams{
		Model: openai.ImageModel("gpt-image-2"),
		Prompt: "A children's book drawing of a veterinarian using a stethoscope to " +
			"listen to the heartbeat of a baby otter.",
	})
	if err != nil {
		panic(err)
	}
	image, err := base64.StdEncoding.DecodeString(result.Data[0].B64JSON)
	if err != nil {
		panic(err)
	}
	if err := os.WriteFile("otter.png", image, 0o600); err != nil {
		panic(err)
	}
}
```

```bash
curl -X POST "https://api.openai.com/v1/images/generations" \
    -H "Authorization: Bearer $OPENAI_API_KEY" \
    -H "Content-type: application/json" \
    -d '{
        "model": "gpt-image-2",
        "prompt": "A children'\''s book drawing of a veterinarian using a stethoscope to listen to the heartbeat of a baby otter."
    }' | jq -r '.data[0].b64_json' | base64 --decode > otter.png
```

```bash
# OpenAI CLI
openai images generate \
  --model gpt-image-2 \
  --prompt "A children's book drawing of a veterinarian using a stethoscope to listen to the heartbeat of a baby otter." \
  --raw-output \
  --transform 'data.0.b64_json' | base64 --decode > otter.png
```

You can set the `n` parameter to generate multiple images at once in a single request (by default, the API returns a single image).

---

## 2. Generate images — Responses API

```javascript
import OpenAI from "openai";
const openai = new OpenAI();

const response = await openai.responses.create({
  model: "gpt-5.6",
  input:
    "Generate an image of gray tabby cat hugging an otter with an orange scarf",
  tools: [{ type: "image_generation" }],
});

// Save the image to a file
const imageData = response.output
  .filter((output) => output.type === "image_generation_call")
  .map((output) => output.result);

if (imageData.length > 0) {
  const imageBase64 = imageData[0];
  const fs = await import("fs");
  fs.writeFileSync("otter.png", Buffer.from(imageBase64, "base64"));
}
```

```python
from openai import OpenAI
import base64

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6",
    input="Generate an image of gray tabby cat hugging an otter with an orange scarf",
    tools=[{"type": "image_generation"}],
)

# Save the image to a file
image_data = [
    output.result
    for output in response.output
    if output.type == "image_generation_call"
]

if image_data:
    image_base64 = image_data[0]
    with open("otter.png", "wb") as f:
        f.write(base64.b64decode(image_base64))
```

```go
package main

import (
	"context"
	"encoding/base64"
	"os"

	"github.com/openai/openai-go/v3"
	"github.com/openai/openai-go/v3/responses"
)

func main() {
	client := openai.NewClient()
	response, err := client.Responses.New(context.Background(), responses.ResponseNewParams{
		Model: "gpt-5.6",
		Input: responses.ResponseNewParamsInputUnion{
			OfString: openai.String("Generate an image of gray tabby cat hugging an otter with an orange scarf"),
		},
		Tools: []responses.ToolUnionParam{{OfImageGeneration: &responses.ToolImageGenerationParam{}}},
	})
	if err != nil {
		panic(err)
	}
	saveFirstGeneratedImage(response, "otter.png")
}

func saveFirstGeneratedImage(response *responses.Response, filename string) {
	for _, output := range response.Output {
		if output.Type != "image_generation_call" {
			continue
		}
		image, err := base64.StdEncoding.DecodeString(output.AsImageGenerationCall().Result)
		if err != nil {
			panic(err)
		}
		if err := os.WriteFile(filename, image, 0o600); err != nil {
			panic(err)
		}
		return
	}
	panic("response did not include an image generation call")
}
```

### Force generate vs. edit with `action`

With the Responses API image generation tool, supported tool models can choose whether to generate a new image or edit one already in the conversation. The optional `action` parameter controls this: `action: "auto"` (default, model decides), `action: "generate"` (always create new), `action: "edit"` (force edit — errors if no image is in context).

```javascript
const response = await openai.responses.create({
  model: "gpt-5.6",
  input:
    "Generate an image of gray tabby cat hugging an otter with an orange scarf",
  tools: [{ type: "image_generation", action: "generate" }],
});
```

```python
response = client.responses.create(
    model="gpt-5.6",
    input="Generate an image of gray tabby cat hugging an otter with an orange scarf",
    tools=[{"type": "image_generation", "action": "generate"}],
)
```

```go
Tools: []responses.ToolUnionParam{{OfImageGeneration: &responses.ToolImageGenerationParam{Action: "generate"}}},
```

---

## 3. Multi-turn image generation

Build multi-turn conversations by either providing prior image generation call outputs in context (or just the image ID), or by using `previous_response_id`. This lets you refine prompts and evolve output across turns.

### Using `previous_response_id`

```javascript
import OpenAI from "openai";
const openai = new OpenAI();

const response = await openai.responses.create({
  model: "gpt-5.6",
  input:
    "Generate an image of gray tabby cat hugging an otter with an orange scarf",
  tools: [{ type: "image_generation" }],
});

const imageData = response.output
  .filter((output) => output.type === "image_generation_call")
  .map((output) => output.result);

if (imageData.length > 0) {
  const imageBase64 = imageData[0];
  const fs = await import("fs");
  fs.writeFileSync("cat_and_otter.png", Buffer.from(imageBase64, "base64"));
}

// Follow up
const response_fwup = await openai.responses.create({
  model: "gpt-5.6",
  previous_response_id: response.id,
  input: "Now make it look realistic",
  tools: [{ type: "image_generation" }],
});

const imageData_fwup = response_fwup.output
  .filter((output) => output.type === "image_generation_call")
  .map((output) => output.result);

if (imageData_fwup.length > 0) {
  const imageBase64 = imageData_fwup[0];
  const fs = await import("fs");
  fs.writeFileSync(
    "cat_and_otter_realistic.png",
    Buffer.from(imageBase64, "base64")
  );
}
```

```python
from openai import OpenAI
import base64

client = OpenAI()

response = client.responses.create(
    model="gpt-5.6",
    input="Generate an image of gray tabby cat hugging an otter with an orange scarf",
    tools=[{"type": "image_generation"}],
)

image_data = [
    output.result
    for output in response.output
    if output.type == "image_generation_call"
]

if image_data:
    image_base64 = image_data[0]
    with open("cat_and_otter.png", "wb") as f:
        f.write(base64.b64decode(image_base64))

# Follow up
response_fwup = client.responses.create(
    model="gpt-5.6",
    previous_response_id=response.id,
    input="Now make it look realistic",
    tools=[{"type": "image_generation"}],
)

image_data_fwup = [
    output.result
    for output in response_fwup.output
    if output.type == "image_generation_call"
]

if image_data_fwup:
    image_base64 = image_data_fwup[0]
    with open("cat_and_otter_realistic.png", "wb") as f:
        f.write(base64.b64decode(image_base64))
```

```go
package main

import (
	"context"
	"encoding/base64"
	"os"

	"github.com/openai/openai-go/v3"
	"github.com/openai/openai-go/v3/responses"
)

func main() {
	client := openai.NewClient()
	first, err := client.Responses.New(context.Background(), responses.ResponseNewParams{
		Model: "gpt-5.6",
		Input: responses.ResponseNewParamsInputUnion{
			OfString: openai.String("Generate an image of gray tabby cat hugging an otter with an orange scarf"),
		},
		Tools: []responses.ToolUnionParam{{OfImageGeneration: &responses.ToolImageGenerationParam{}}},
	})
	if err != nil {
		panic(err)
	}
	saveFirstGeneratedImage(first, "cat_and_otter.png")

	followUp, err := client.Responses.New(context.Background(), responses.ResponseNewParams{
		Model:              "gpt-5.6",
		PreviousResponseID: openai.String(first.ID),
		Input: responses.ResponseNewParamsInputUnion{
			OfString: openai.String("Now make it look realistic"),
		},
		Tools: []responses.ToolUnionParam{{OfImageGeneration: &responses.ToolImageGenerationParam{}}},
	})
	if err != nil {
		panic(err)
	}
	saveFirstGeneratedImage(followUp, "cat_and_otter_realistic.png")
}

func saveFirstGeneratedImage(response *responses.Response, filename string) {
	for _, output := range response.Output {
		if output.Type != "image_generation_call" {
			continue
		}
		image, err := base64.StdEncoding.DecodeString(output.AsImageGenerationCall().Result)
		if err != nil {
			panic(err)
		}
		if err := os.WriteFile(filename, image, 0o600); err != nil {
			panic(err)
		}
		return
	}
	panic("response did not include an image generation call")
}
```

### Using image ID (carry prior call in `input` instead of `previous_response_id`)

```javascript
import OpenAI from "openai";
const openai = new OpenAI();

const response = await openai.responses.create({
  model: "gpt-5.6",
  input:
    "Generate an image of gray tabby cat hugging an otter with an orange scarf",
  tools: [{ type: "image_generation" }],
});

const imageGenerationCalls = response.output.filter(
  (output) => output.type === "image_generation_call"
);

const imageData = imageGenerationCalls.map((output) => output.result);

if (imageData.length > 0) {
  const imageBase64 = imageData[0];
  const fs = await import("fs");
  fs.writeFileSync("cat_and_otter.png", Buffer.from(imageBase64, "base64"));
}

// Follow up
const response_fwup = await openai.responses.create({
  model: "gpt-5.6",
  input: [
    {
      role: "user",
      content: [{ type: "input_text", text: "Now make it look realistic" }],
    },
    {
      type: "image_generation_call",
      id: imageGenerationCalls[0].id,
    },
  ],
  tools: [{ type: "image_generation" }],
});

const imageData_fwup = response_fwup.output
  .filter((output) => output.type === "image_generation_call")
  .map((output) => output.result);

if (imageData_fwup.length > 0) {
  const imageBase64 = imageData_fwup[0];
  const fs = await import("fs");
  fs.writeFileSync(
    "cat_and_otter_realistic.png",
    Buffer.from(imageBase64, "base64")
  );
}
```

```python
import openai
import base64

response = openai.responses.create(
    model="gpt-5.6",
    input="Generate an image of gray tabby cat hugging an otter with an orange scarf",
    tools=[{"type": "image_generation"}],
)

image_generation_calls = [
    output for output in response.output if output.type == "image_generation_call"
]

image_data = [output.result for output in image_generation_calls]

if image_data:
    image_base64 = image_data[0]
    with open("cat_and_otter.png", "wb") as f:
        f.write(base64.b64decode(image_base64))

# Follow up
response_fwup = openai.responses.create(
    model="gpt-5.6",
    input=[
        {
            "role": "user",
            "content": [{"type": "input_text", "text": "Now make it look realistic"}],
        },
        {
            "type": "image_generation_call",
            "id": image_generation_calls[0].id,
        },
    ],
    tools=[{"type": "image_generation"}],
)

image_data_fwup = [
    output.result
    for output in response_fwup.output
    if output.type == "image_generation_call"
]

if image_data_fwup:
    image_base64 = image_data_fwup[0]
    with open("cat_and_otter_realistic.png", "wb") as f:
        f.write(base64.b64decode(image_base64))
```

```go
package main

import (
	"context"
	"encoding/base64"
	"encoding/json"
	"os"

	"github.com/openai/openai-go/v3"
	"github.com/openai/openai-go/v3/responses"
)

func main() {
	client := openai.NewClient()
	first, err := client.Responses.New(context.Background(), responses.ResponseNewParams{
		Model: "gpt-5.6",
		Input: responses.ResponseNewParamsInputUnion{
			OfString: openai.String("Generate an image of gray tabby cat hugging an otter with an orange scarf"),
		},
		Tools: []responses.ToolUnionParam{{OfImageGeneration: &responses.ToolImageGenerationParam{}}},
	})
	if err != nil {
		panic(err)
	}
	call := firstImageGenerationCall(first)
	saveImage("cat_and_otter.png", call.Result)
	input := outputAsInput(first.Output)
	input = append(input, responses.ResponseInputItemParamOfMessage(
		responses.ResponseInputMessageContentListParam{responses.ResponseInputContentParamOfInputText("Now make it look realistic")},
		responses.EasyInputMessageRoleUser,
	))

	followUp, err := client.Responses.New(context.Background(), responses.ResponseNewParams{
		Model: "gpt-5.6",
		Input: responses.ResponseNewParamsInputUnion{OfInputItemList: input},
		Tools: []responses.ToolUnionParam{{OfImageGeneration: &responses.ToolImageGenerationParam{}}},
	})
	if err != nil {
		panic(err)
	}
	saveImage("cat_and_otter_realistic.png", firstImageGenerationCall(followUp).Result)
}

func firstImageGenerationCall(response *responses.Response) responses.ResponseOutputItemImageGenerationCall {
	for _, output := range response.Output {
		if output.Type == "image_generation_call" {
			return output.AsImageGenerationCall()
		}
	}
	panic("response did not include an image generation call")
}

func outputAsInput(output []responses.ResponseOutputItemUnion) []responses.ResponseInputItemUnionParam {
	input := make([]responses.ResponseInputItemUnionParam, 0, len(output))
	for _, item := range output {
		var converted responses.ResponseInputItemUnion
		if err := json.Unmarshal([]byte(item.RawJSON()), &converted); err != nil {
			panic(err)
		}
		input = append(input, converted.ToParam())
	}
	return input
}

func saveImage(filename, encoded string) {
	image, err := base64.StdEncoding.DecodeString(encoded)
	if err != nil {
		panic(err)
	}
	if err := os.WriteFile(filename, image, 0o600); err != nil {
		panic(err)
	}
}
```

---

## 4. Streaming

Both APIs support streaming partial images as they're generated. Adjust `partial_images` to receive 0–3 partials. `partial_images: 0` means only the final image; for values >0 you may receive fewer partials than requested if generation finishes quickly.

### Responses API

```javascript
import OpenAI from "openai";
import fs from "fs";
const openai = new OpenAI();

function saveBase64Image(filename, imageBase64) {
  const imageBuffer = Buffer.from(imageBase64, "base64");
  fs.writeFileSync(filename, imageBuffer);
}

const stream = await openai.responses.create({
  model: "gpt-5.6",
  input:
    "Draw a gorgeous image of a river made of white owl feathers, snaking its way through a serene winter landscape",
  stream: true,
  tools: [{ type: "image_generation", partial_images: 2 }],
});

for await (const event of stream) {
  if (event.type === "response.image_generation_call.partial_image") {
    const idx = event.partial_image_index;
    saveBase64Image(`river-partial-${idx}.png`, event.partial_image_b64);
  } else if (event.type === "response.completed") {
    const imageData = event.response.output
      .filter((output) => output.type === "image_generation_call")
      .map((output) => output.result);

    if (imageData.length > 0) {
      saveBase64Image("river-final.png", imageData[0]);
    }
  }
}
```

```python
from openai import OpenAI
import base64

client = OpenAI()


def save_base64_image(filename, image_base64):
    image_bytes = base64.b64decode(image_base64)
    with open(filename, "wb") as f:
        f.write(image_bytes)


stream = client.responses.create(
    model="gpt-5.6",
    input="Draw a gorgeous image of a river made of white owl feathers, snaking its way through a serene winter landscape",
    stream=True,
    tools=[{"type": "image_generation", "partial_images": 2}],
)

for event in stream:
    if event.type == "response.image_generation_call.partial_image":
        idx = event.partial_image_index
        save_base64_image(f"river-partial-{idx}.png", event.partial_image_b64)
    elif event.type == "response.completed":
        image_data = [
            output.result
            for output in event.response.output
            if output.type == "image_generation_call"
        ]

        if image_data:
            save_base64_image("river-final.png", image_data[0])
```

```go
package main

import (
	"context"
	"encoding/base64"
	"fmt"
	"os"

	"github.com/openai/openai-go/v3"
	"github.com/openai/openai-go/v3/responses"
)

func main() {
	client := openai.NewClient()
	stream := client.Responses.NewStreaming(context.Background(), responses.ResponseNewParams{
		Model: "gpt-5.6",
		Input: responses.ResponseNewParamsInputUnion{
			OfString: openai.String("Draw a gorgeous image of a river made of white owl feathers, snaking its way through a serene winter landscape"),
		},
		Tools: []responses.ToolUnionParam{{OfImageGeneration: &responses.ToolImageGenerationParam{PartialImages: openai.Int(2)}}},
	})
	for stream.Next() {
		event := stream.Current()
		if event.Type == "response.image_generation_call.partial_image" {
			partial := event.AsResponseImageGenerationCallPartialImage()
			saveImage(fmt.Sprintf("river-partial-%d.png", partial.PartialImageIndex), partial.PartialImageB64)
		}
		if event.Type == "response.completed" {
			for _, output := range event.AsResponseCompleted().Response.Output {
				if output.Type == "image_generation_call" {
					saveImage("river-final.png", output.AsImageGenerationCall().Result)
				}
			}
		}
	}
	if err := stream.Err(); err != nil {
		panic(err)
	}
}

func saveImage(filename, encoded string) {
	image, err := base64.StdEncoding.DecodeString(encoded)
	if err != nil {
		panic(err)
	}
	if err := os.WriteFile(filename, image, 0o600); err != nil {
		panic(err)
	}
}
```

### Image API

```javascript
import fs from "fs";
import OpenAI from "openai";

const openai = new OpenAI();

const prompt =
  "Draw a gorgeous image of a river made of white owl feathers, snaking its way through a serene winter landscape";
const stream = await openai.images.generate({
  prompt: prompt,
  model: "gpt-image-2",
  stream: true,
  partial_images: 2,
});

for await (const event of stream) {
  if (event.type === "image_generation.partial_image") {
    const idx = event.partial_image_index;
    const imageBase64 = event.b64_json;
    const imageBuffer = Buffer.from(imageBase64, "base64");
    fs.writeFileSync(`river${idx}.png`, imageBuffer);
  }
}
```

```python
from openai import OpenAI
import base64

client = OpenAI()

stream = client.images.generate(
    prompt="Draw a gorgeous image of a river made of white owl feathers, snaking its way through a serene winter landscape",
    model="gpt-image-2",
    stream=True,
    partial_images=2,
)

for event in stream:
    if event.type == "image_generation.partial_image":
        idx = event.partial_image_index
        image_base64 = event.b64_json
        image_bytes = base64.b64decode(image_base64)
        with open(f"river{idx}.png", "wb") as f:
            f.write(image_bytes)
```

```go
package main

import (
	"context"
	"encoding/base64"
	"fmt"
	"os"

	"github.com/openai/openai-go/v3"
)

func main() {
	client := openai.NewClient()
	stream := client.Images.GenerateStreaming(context.Background(), openai.ImageGenerateParams{
		Model:         openai.ImageModel("gpt-image-2"),
		Prompt:        "Draw a gorgeous image of a river made of white owl feathers, snaking its way through a serene winter landscape",
		PartialImages: openai.Int(2),
	})
	for stream.Next() {
		event := stream.Current()
		if event.Type != "image_generation.partial_image" {
			continue
		}
		partial := event.AsImageGenerationPartialImage()
		saveImage(fmt.Sprintf("river%d.png", partial.PartialImageIndex), partial.B64JSON)
	}
	if err := stream.Err(); err != nil {
		panic(err)
	}
}

func saveImage(filename, encoded string) {
	image, err := base64.StdEncoding.DecodeString(encoded)
	if err != nil {
		panic(err)
	}
	if err := os.WriteFile(filename, image, 0o600); err != nil {
		panic(err)
	}
}
```

---

## 5. Revised prompt

When using the image generation tool in the Responses API, the mainline model (e.g. `gpt-5.5`) automatically revises your prompt for improved performance. Access it via the `revised_prompt` field on the image generation call:

```json
{
  "id": "ig_123",
  "type": "image_generation_call",
  "status": "completed",
  "revised_prompt": "A gray tabby cat hugging an otter. The otter is wearing an orange scarf. Both animals are cute and friendly, depicted in a warm, heartwarming style.",
  "result": "..."
}
```

---

## 6. Edit images — reference images (Responses API)

The edits capability lets you: edit existing images, generate new images using other images as reference, and edit parts of an image via a mask. This example uses 4 input images to generate a new image of a gift basket containing the items in the reference images.

With the Responses API, provide input images 3 ways: a fully-qualified URL, a base64-encoded data URL, or a file ID (via the Files API).

### Create a File

```javascript
import fs from "fs";
import OpenAI from "openai";

const openai = new OpenAI();

async function createFile(filePath) {
  const fileContent = fs.createReadStream(filePath);
  const result = await openai.files.create({
    file: fileContent,
    purpose: "vision",
  });
  return result.id;
}
```

```python
from openai import OpenAI

client = OpenAI()


def create_file(file_path):
    with open(file_path, "rb") as file_content:
        result = client.files.create(
            file=file_content,
            purpose="vision",
        )
        return result.id
```

```go
package main

import (
	"context"
	"fmt"
	"os"

	"github.com/openai/openai-go/v3"
)

func main() {
	client := openai.NewClient()
	file, err := os.Open("image.png")
	if err != nil {
		panic(err)
	}
	defer file.Close()

	uploaded, err := client.Files.New(context.Background(), openai.FileNewParams{
		File:    file,
		Purpose: openai.FilePurposeVision,
	})
	if err != nil {
		panic(err)
	}
	fmt.Println(uploaded.ID)
}
```

### Create a base64-encoded image

```javascript
import fs from "fs";

function encodeImage(filePath) {
  const base64Image = fs.readFileSync(filePath, "base64");
  return base64Image;
}
```

```python
import base64


def encode_image(file_path):
    with open(file_path, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode("utf-8")
    return base64_image
```

```go
package main

import (
	"encoding/base64"
	"fmt"
	"os"
)

func main() {
	image, err := os.ReadFile("image.png")
	if err != nil {
		panic(err)
	}
	fmt.Println(base64.StdEncoding.EncodeToString(image))
}
```

### Edit / combine reference images

```javascript
import fs from "fs";
import OpenAI from "openai";

const openai = new OpenAI();

function encodeImage(filePath) {
  return fs.readFileSync(filePath, "base64");
}

async function createFile(filePath) {
  const result = await openai.files.create({
    file: fs.createReadStream(filePath),
    purpose: "vision",
  });
  return result.id;
}

const prompt = `Generate a photorealistic image of a gift basket on a white background
labeled 'Relax & Unwind' with a ribbon and handwriting-like font,
containing all the items in the reference pictures.`;

const base64Image1 = encodeImage("fixtures/body-lotion.png");
const base64Image2 = encodeImage("fixtures/soap.png");
const fileId1 = await createFile("fixtures/bath-bomb.png");
const fileId2 = await createFile("fixtures/incense-kit.png");

const response = await openai.responses.create({
  model: "gpt-5.6",
  input: [
    {
      role: "user",
      content: [
        { type: "input_text", text: prompt },
        {
          type: "input_image",
          image_url: `data:image/png;base64,${base64Image1}`,
          detail: "auto",
        },
        {
          type: "input_image",
          image_url: `data:image/png;base64,${base64Image2}`,
          detail: "auto",
        },
        {
          type: "input_image",
          file_id: fileId1,
          detail: "auto",
        },
        {
          type: "input_image",
          file_id: fileId2,
          detail: "auto",
        },
      ],
    },
  ],
  tools: [{ type: "image_generation" }],
});

const imageData = response.output
  .filter((output) => output.type === "image_generation_call")
  .map((output) => output.result);

if (imageData.length > 0) {
  const imageBase64 = imageData[0];
  fs.writeFileSync("gift-basket.png", Buffer.from(imageBase64, "base64"));
} else {
  console.log(response.output_text);
}
```

```python
from openai import OpenAI
import base64

client = OpenAI()


def encode_image(file_path):
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def create_file(file_path):
    with open(file_path, "rb") as file_content:
        result = client.files.create(file=file_content, purpose="vision")
    return result.id


prompt = """Generate a photorealistic image of a gift basket on a white background
labeled 'Relax & Unwind' with a ribbon and handwriting-like font,
containing all the items in the reference pictures."""

base64_image1 = encode_image("body-lotion.png")
base64_image2 = encode_image("soap.png")
file_id1 = create_file("bath-bomb.png")
file_id2 = create_file("incense-kit.png")

response = client.responses.create(
    model="gpt-5.6",
    input=[
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {
                    "type": "input_image",
                    "image_url": f"data:image/png;base64,{base64_image1}",
                },
                {
                    "type": "input_image",
                    "image_url": f"data:image/png;base64,{base64_image2}",
                },
                {
                    "type": "input_image",
                    "file_id": file_id1,
                },
                {
                    "type": "input_image",
                    "file_id": file_id2,
                },
            ],
        }
    ],
    tools=[{"type": "image_generation"}],
)

image_generation_calls = [
    output for output in response.output if output.type == "image_generation_call"
]

image_data = [output.result for output in image_generation_calls]

if image_data:
    image_base64 = image_data[0]
    with open("gift-basket.png", "wb") as f:
        f.write(base64.b64decode(image_base64))
else:
    print(response.output_text)
```

```go
package main

import (
	"context"
	"encoding/base64"
	"os"

	"github.com/openai/openai-go/v3"
	"github.com/openai/openai-go/v3/responses"
)

func main() {
	client := openai.NewClient()
	bathBombID := uploadImage(client, "bath-bomb.png")
	incenseKitID := uploadImage(client, "incense-kit.png")

	response, err := client.Responses.New(context.Background(), responses.ResponseNewParams{
		Model: "gpt-5.6",
		Input: responses.ResponseNewParamsInputUnion{OfInputItemList: responses.ResponseInputParam{
			responses.ResponseInputItemParamOfMessage(
				responses.ResponseInputMessageContentListParam{
					responses.ResponseInputContentParamOfInputText("Generate a photorealistic image of a gift basket on a white background labeled 'Relax & Unwind' with a ribbon and handwriting-like font, containing all the items in the reference pictures."),
					{OfInputImage: &responses.ResponseInputImageParam{ImageURL: openai.String(dataURL("body-lotion.png")), Detail: responses.ResponseInputImageDetailAuto}},
					{OfInputImage: &responses.ResponseInputImageParam{ImageURL: openai.String(dataURL("soap.png")), Detail: responses.ResponseInputImageDetailAuto}},
					{OfInputImage: &responses.ResponseInputImageParam{FileID: openai.String(bathBombID), Detail: responses.ResponseInputImageDetailAuto}},
					{OfInputImage: &responses.ResponseInputImageParam{FileID: openai.String(incenseKitID), Detail: responses.ResponseInputImageDetailAuto}},
				},
				responses.EasyInputMessageRoleUser,
			),
		}},
		Tools: []responses.ToolUnionParam{{OfImageGeneration: &responses.ToolImageGenerationParam{}}},
	})
	if err != nil {
		panic(err)
	}
	saveFirstGeneratedImage(response, "gift-basket.png")
}

func uploadImage(client openai.Client, filename string) string {
	file, err := os.Open(filename)
	if err != nil {
		panic(err)
	}
	defer file.Close()
	uploaded, err := client.Files.New(context.Background(), openai.FileNewParams{File: file, Purpose: openai.FilePurposeVision})
	if err != nil {
		panic(err)
	}
	return uploaded.ID
}

func dataURL(filename string) string {
	image, err := os.ReadFile(filename)
	if err != nil {
		panic(err)
	}
	return "data:image/png;base64," + base64.StdEncoding.EncodeToString(image)
}

func saveFirstGeneratedImage(response *responses.Response, filename string) {
	for _, output := range response.Output {
		if output.Type != "image_generation_call" {
			continue
		}
		image, err := base64.StdEncoding.DecodeString(output.AsImageGenerationCall().Result)
		if err != nil {
			panic(err)
		}
		if err := os.WriteFile(filename, image, 0o600); err != nil {
			panic(err)
		}
		return
	}
	panic("response did not include an image generation call")
}
```

---

## 7. Edit images — reference images (Image API)

```javascript
import fs from "fs";
import OpenAI, { toFile } from "openai";

const client = new OpenAI();

const prompt = `
Generate a photorealistic image of a gift basket on a white background
labeled 'Relax & Unwind' with a ribbon and handwriting-like font,
containing all the items in the reference pictures.
`;

const imageFiles = [
  "fixtures/bath-bomb.png",
  "fixtures/body-lotion.png",
  "fixtures/incense-kit.png",
  "fixtures/soap.png",
];

const images = await Promise.all(
  imageFiles.map(
    async (file) =>
      await toFile(fs.createReadStream(file), null, {
        type: "image/png",
      })
  )
);

const response = await client.images.edit({
  model: "gpt-image-2",
  image: images,
  prompt,
});

// Save the image to a file
const image_base64 = response.data[0].b64_json;
const image_bytes = Buffer.from(image_base64, "base64");
fs.writeFileSync("basket.png", image_bytes);
```

```python
import base64
from openai import OpenAI

client = OpenAI()

prompt = """
Generate a photorealistic image of a gift basket on a white background
labeled 'Relax & Unwind' with a ribbon and handwriting-like font,
containing all the items in the reference pictures.
"""

result = client.images.edit(
    model="gpt-image-2",
    image=[
        open("body-lotion.png", "rb"),
        open("bath-bomb.png", "rb"),
        open("incense-kit.png", "rb"),
        open("soap.png", "rb"),
    ],
    prompt=prompt,
)

image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

# Save the image to a file
with open("gift-basket.png", "wb") as f:
    f.write(image_bytes)
```

```go
package main

import (
	"context"
	"encoding/base64"
	"io"
	"os"

	"github.com/openai/openai-go/v3"
)

func main() {
	client := openai.NewClient()
	files, closeFiles := openImages(
		"bath-bomb.png",
		"body-lotion.png",
		"incense-kit.png",
		"soap.png",
	)
	defer closeFiles()

	response, err := client.Images.Edit(context.Background(), openai.ImageEditParams{
		Model: openai.ImageModel("gpt-image-2"),
		Image: openai.ImageEditParamsImageUnion{OfFileArray: files},
		Prompt: "Generate a photorealistic image of a gift basket on a white background " +
			"labeled 'Relax & Unwind' with a ribbon and handwriting-like font, containing all the items in the reference pictures.",
	})
	if err != nil {
		panic(err)
	}
	saveImage("basket.png", response.Data[0].B64JSON)
}

func openImages(names ...string) ([]io.Reader, func()) {
	images := make([]io.Reader, 0, len(names))
	files := make([]*os.File, 0, len(names))
	for _, name := range names {
		file, err := os.Open(name)
		if err != nil {
			closeFiles(files)
			panic(err)
		}
		images = append(images, openai.File(file, name, "image/png"))
		files = append(files, file)
	}
	return images, func() { closeFiles(files) }
}

func closeFiles(files []*os.File) {
	for _, file := range files {
		if err := file.Close(); err != nil {
			panic(err)
		}
	}
}

func saveImage(filename, encoded string) {
	image, err := base64.StdEncoding.DecodeString(encoded)
	if err != nil {
		panic(err)
	}
	if err := os.WriteFile(filename, image, 0o600); err != nil {
		panic(err)
	}
}
```

```bash
curl -s -D >(grep -i x-request-id >&2) \
  -o >(jq -r '.data[0].b64_json' | base64 --decode > gift-basket.png) \
  -X POST "https://api.openai.com/v1/images/edits" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F "model=gpt-image-2" \
  -F "image[]=@body-lotion.png" \
  -F "image[]=@bath-bomb.png" \
  -F "image[]=@incense-kit.png" \
  -F "image[]=@soap.png" \
  -F 'prompt=Generate a photorealistic image of a gift basket on a white background labeled "Relax & Unwind" with a ribbon and handwriting-like font, containing all the items in the reference pictures'
```

```bash
# OpenAI CLI
openai images edit \
  --model gpt-image-2 \
  --image body-lotion.png \
  --image bath-bomb.png \
  --image incense-kit.png \
  --image soap.png \
  --prompt 'Generate a photorealistic image of a gift basket on a white background labeled "Relax & Unwind" with a ribbon and handwriting-like font, containing all the items in the reference pictures' \
  --raw-output \
  --transform 'data.0.b64_json' | base64 --decode > gift-basket.png
```

---

## 8. Edit images with a mask

Provide a mask to indicate which part of the image should be edited. Masking with GPT Image is entirely **prompt-based** — the model uses the mask as guidance but may not follow its exact shape with complete precision. If you provide multiple input images, the mask applies to the first one only.

### Responses API

```javascript
import fs from "fs";
import OpenAI from "openai";

const openai = new OpenAI();

async function createFile(filePath) {
  const result = await openai.files.create({
    file: fs.createReadStream(filePath),
    purpose: "vision",
  });
  return result.id;
}

const fileId = await createFile("fixtures/sunlit_lounge.png");
const maskId = await createFile("fixtures/mask.png");

const response = await openai.responses.create({
  model: "gpt-5.6",
  input: [
    {
      role: "user",
      content: [
        {
          type: "input_text",
          text: "generate an image of the same sunlit indoor lounge area with a pool but the pool should contain a flamingo",
        },
        {
          type: "input_image",
          file_id: fileId,
          detail: "auto",
        },
      ],
    },
  ],
  tools: [
    {
      type: "image_generation",
      quality: "high",
      input_image_mask: {
        file_id: maskId,
      },
    },
  ],
});

const imageData = response.output
  .filter((output) => output.type === "image_generation_call")
  .map((output) => output.result);

if (imageData.length > 0) {
  const imageBase64 = imageData[0];
  fs.writeFileSync("lounge.png", Buffer.from(imageBase64, "base64"));
}
```

```python
from openai import OpenAI
import base64

client = OpenAI()


def create_file(file_path):
    with open(file_path, "rb") as file_content:
        result = client.files.create(file=file_content, purpose="vision")
    return result.id


fileId = create_file("sunlit_lounge.png")
maskId = create_file("mask.png")

response = client.responses.create(
    model="gpt-5.6",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": "generate an image of the same sunlit indoor lounge area with a pool but the pool should contain a flamingo",
                },
                {
                    "type": "input_image",
                    "file_id": fileId,
                },
            ],
        },
    ],
    tools=[
        {
            "type": "image_generation",
            "quality": "high",
            "input_image_mask": {
                "file_id": maskId,
            },
        },
    ],
)

image_data = [
    output.result
    for output in response.output
    if output.type == "image_generation_call"
]

if image_data:
    image_base64 = image_data[0]
    with open("lounge.png", "wb") as f:
        f.write(base64.b64decode(image_base64))
```

```go
package main

import (
	"context"
	"encoding/base64"
	"os"

	"github.com/openai/openai-go/v3"
	"github.com/openai/openai-go/v3/responses"
)

func main() {
	client := openai.NewClient()
	imageID := uploadImage(client, "sunlit_lounge.png")
	maskID := uploadImage(client, "mask.png")
	response, err := client.Responses.New(context.Background(), responses.ResponseNewParams{
		Model: "gpt-5.6",
		Input: responses.ResponseNewParamsInputUnion{OfInputItemList: responses.ResponseInputParam{
			responses.ResponseInputItemParamOfMessage(
				responses.ResponseInputMessageContentListParam{
					responses.ResponseInputContentParamOfInputText("Generate an image of the same sunlit indoor lounge area with a pool, but the pool should contain a flamingo."),
					{OfInputImage: &responses.ResponseInputImageParam{FileID: openai.String(imageID), Detail: responses.ResponseInputImageDetailAuto}},
				},
				responses.EasyInputMessageRoleUser,
			),
		}},
		Tools: []responses.ToolUnionParam{{OfImageGeneration: &responses.ToolImageGenerationParam{
			Quality:        "high",
			InputImageMask: responses.ToolImageGenerationInputImageMaskParam{FileID: openai.String(maskID)},
		}}},
	})
	if err != nil {
		panic(err)
	}
	saveFirstGeneratedImage(response, "lounge.png")
}

func uploadImage(client openai.Client, filename string) string {
	file, err := os.Open(filename)
	if err != nil {
		panic(err)
	}
	defer file.Close()
	uploaded, err := client.Files.New(context.Background(), openai.FileNewParams{File: file, Purpose: openai.FilePurposeVision})
	if err != nil {
		panic(err)
	}
	return uploaded.ID
}

func saveFirstGeneratedImage(response *responses.Response, filename string) {
	for _, output := range response.Output {
		if output.Type != "image_generation_call" {
			continue
		}
		image, err := base64.StdEncoding.DecodeString(output.AsImageGenerationCall().Result)
		if err != nil {
			panic(err)
		}
		if err := os.WriteFile(filename, image, 0o600); err != nil {
			panic(err)
		}
		return
	}
	panic("response did not include an image generation call")
}
```

### Image API

```javascript
import fs from "fs";
import OpenAI, { toFile } from "openai";

const client = new OpenAI();

const rsp = await client.images.edit({
  model: "gpt-image-2",
  image: await toFile(fs.createReadStream("fixtures/sunlit_lounge.png"), null, {
    type: "image/png",
  }),
  mask: await toFile(fs.createReadStream("fixtures/mask.png"), null, {
    type: "image/png",
  }),
  prompt: "A sunlit indoor lounge area with a pool containing a flamingo",
});

// Save the image to a file
const image_base64 = rsp.data[0].b64_json;
const image_bytes = Buffer.from(image_base64, "base64");
fs.writeFileSync("lounge.png", image_bytes);
```

```python
from openai import OpenAI
import base64

client = OpenAI()

result = client.images.edit(
    model="gpt-image-2",
    image=open("sunlit_lounge.png", "rb"),
    mask=open("mask.png", "rb"),
    prompt="A sunlit indoor lounge area with a pool containing a flamingo",
)

image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

# Save the image to a file
with open("composition.png", "wb") as f:
    f.write(image_bytes)
```

```go
package main

import (
	"context"
	"encoding/base64"
	"os"

	"github.com/openai/openai-go/v3"
)

func main() {
	client := openai.NewClient()
	image, err := os.Open("sunlit_lounge.png")
	if err != nil {
		panic(err)
	}
	defer image.Close()
	mask, err := os.Open("mask.png")
	if err != nil {
		panic(err)
	}
	defer mask.Close()

	response, err := client.Images.Edit(context.Background(), openai.ImageEditParams{
		Model:  openai.ImageModel("gpt-image-2"),
		Image:  openai.ImageEditParamsImageUnion{OfFile: openai.File(image, "sunlit_lounge.png", "image/png")},
		Mask:   openai.File(mask, "mask.png", "image/png"),
		Prompt: "A sunlit indoor lounge area with a pool containing a flamingo",
	})
	if err != nil {
		panic(err)
	}
	result, err := base64.StdEncoding.DecodeString(response.Data[0].B64JSON)
	if err != nil {
		panic(err)
	}
	if err := os.WriteFile("lounge.png", result, 0o600); err != nil {
		panic(err)
	}
}
```

```bash
curl -s -D >(grep -i x-request-id >&2) \
  -o >(jq -r '.data[0].b64_json' | base64 --decode > lounge.png) \
  -X POST "https://api.openai.com/v1/images/edits" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -F "model=gpt-image-2" \
  -F "mask=@mask.png" \
  -F "image[]=@sunlit_lounge.png" \
  -F 'prompt=A sunlit indoor lounge area with a pool containing a flamingo'
```

```bash
# OpenAI CLI
openai images edit \
  --model gpt-image-2 \
  --image sunlit_lounge.png \
  --mask mask.png \
  --prompt "A sunlit indoor lounge area with a pool containing a flamingo" \
  --raw-output \
  --transform 'data.0.b64_json' | base64 --decode > out.png
```

---

## 9. Mask requirements & adding an alpha channel

The image to edit and the mask must be the **same format and size**, and under **50MB**. The mask image must contain an **alpha channel** — if using an image editor to make the mask, save with an alpha channel. You can also add one programmatically from a black-and-white mask:

```python
from PIL import Image
from io import BytesIO

# 1. Load your black & white mask as a grayscale image
mask = Image.open("mask.png").convert("L")

# 2. Convert it to RGBA so it has space for an alpha channel
mask_rgba = mask.convert("RGBA")

# 3. Then use the mask itself to fill that alpha channel
mask_rgba.putalpha(mask)

# 4. Convert the mask into bytes
buf = BytesIO()
mask_rgba.save(buf, format="PNG")
mask_bytes = buf.getvalue()

# 5. Save the resulting file
img_path_mask_alpha = "mask_alpha.png"
with open(img_path_mask_alpha, "wb") as f:
    f.write(mask_bytes)
```

```go
package main

import (
	"image"
	"image/color"
	"image/png"
	"os"
)

func main() {
	file, err := os.Open("mask.png")
	if err != nil {
		panic(err)
	}
	defer file.Close()

	mask, _, err := image.Decode(file)
	if err != nil {
		panic(err)
	}
	bounds := mask.Bounds()
	withAlpha := image.NewNRGBA(bounds)
	for y := bounds.Min.Y; y < bounds.Max.Y; y++ {
		for x := bounds.Min.X; x < bounds.Max.X; x++ {
			gray := color.GrayModel.Convert(mask.At(x, y)).(color.Gray)
			withAlpha.SetNRGBA(x, y, color.NRGBA{R: gray.Y, G: gray.Y, B: gray.Y, A: gray.Y})
		}
	}

	output, err := os.Create("mask_alpha.png")
	if err != nil {
		panic(err)
	}
	if err := png.Encode(output, withAlpha); err != nil {
		panic(err)
	}
	if err := output.Close(); err != nil {
		panic(err)
	}
}
```

---

## 10. Image input fidelity

The `input_fidelity` parameter controls how strongly a model preserves details from input images during edits and reference-image workflows. **For `gpt-image-2`, omit this parameter** — the API doesn't allow changing it because the model always processes every image input at high fidelity automatically. This means edit requests with reference images can use more input tokens on `gpt-image-2` than you might expect — factor that into cost estimates.

---

## 11. Handling blocked requests and errors

Handle image generation failures like other API errors: check HTTP status or SDK exception type, log the request ID, and consult the error codes guide for auth/quota/rate-limit/server failures. Retry `429`/`5xx` (transient), but not user errors that require changing the request.

Some failures are user-correctable and return `error.type = "image_generation_user_error"`. Don't auto-retry these without modifying the prompt/inputs — use `error.code` as the stable discriminator.

When `error.code = "moderation_blocked"`, the error may include `error.moderation_details`:

```json
{
  "error": {
    "type": "image_generation_user_error",
    "code": "moderation_blocked",
    "moderation_details": {
      "moderation_stage": "input",
      "categories": ["harassment"]
    }
  }
}
```

`moderation_details` gives coarse debugging context without exposing internal classifier labels/scores.

- `moderation_stage`: `input` (blocked at prompt/request inputs) | `output` (blocked at generated image / downstream moderation) | `unknown` (rare fallback).
- `categories`: coarse public labels, e.g. `harassment`, `self-harm`, `sexual`, `violence`.

Keep the primary end-user message generic; use `moderation_details` for developer logs, support workflows, analytics, and light remediation hints. E.g., if `harassment` appears, suggest removing abusive/targeting language; if blocked at `input`, guide the user to revise the prompt; if blocked at `output`, treat it as a generated-result safety block for logging purposes. Always branch on `error.code = "moderation_blocked"` first; treat `moderation_details` as optional extra context.

```javascript
import OpenAI from "openai";

const openai = new OpenAI();

try {
  // The same error handling pattern applies to image generation requests,
  // image edits, and Responses API tool calls that generate images.
  await openai.images.generate({
    model: "gpt-image-2",
    prompt: "Create a poster humiliating my coworker with insulting captions",
  });
} catch (error) {
  if (error?.code !== "moderation_blocked") {
    throw error;
  }

  const moderationDetails = error?.moderation_details;
  const categories = moderationDetails?.categories ?? [];
  const stage = moderationDetails?.moderation_stage;

  let hint =
    "This request could not be completed because it did not meet safety requirements.";

  if (categories.includes("harassment")) {
    hint =
      "Try removing abusive or targeting language and focus on neutral visual details instead.";
  } else if (stage === "input") {
    hint =
      "Try revising the prompt or input images and submit the request again.";
  } else if (stage === "output") {
    hint =
      "The generated result was blocked by a safety check. Try changing the prompt and generating again.";
  }

  console.error("Image generation blocked", {
    request_id: error?.request_id,
    code: error?.code,
    moderation_details: moderationDetails,
  });

  console.log(hint);
}
```

```python
import openai
from openai import OpenAI

client = OpenAI()

try:
    # The same error handling pattern applies to image generation requests,
    # image edits, and Responses API tool calls that generate images.
    client.images.generate(
        model="gpt-image-2",
        prompt="Create a poster humiliating my coworker with insulting captions",
    )
except openai.BadRequestError as error:
    if error.code != "moderation_blocked":
        raise

    error_body = error.body if isinstance(error.body, dict) else {}
    moderation_details = error_body.get("moderation_details") or {}
    categories = moderation_details.get("categories") or []
    stage = moderation_details.get("moderation_stage")

    hint = "This request could not be completed because it did not meet safety requirements."

    if "harassment" in categories:
        hint = "Try removing abusive or targeting language and focus on neutral visual details instead."
    elif stage == "input":
        hint = "Try revising the prompt or input images and submit the request again."
    elif stage == "output":
        hint = "The generated result was blocked by a safety check. Try changing the prompt and generating again."

    print(
        "Image generation blocked",
        {
            "request_id": error.request_id,
            "code": error.code,
            "moderation_details": moderation_details,
        },
    )

    print(hint)
```

```go
package main

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"slices"

	"github.com/openai/openai-go/v3"
)

func main() {
	client := openai.NewClient()
	_, err := client.Images.Generate(context.Background(), openai.ImageGenerateParams{
		Model:  openai.ImageModel("gpt-image-2"),
		Prompt: "Create a poster humiliating my coworker with insulting captions",
	})
	if err == nil {
		return
	}

	var apiError *openai.Error
	if !errors.As(err, &apiError) || apiError.Code != "moderation_blocked" {
		panic(err)
	}

	var body struct {
		ModerationDetails struct {
			Categories      []string `json:"categories"`
			ModerationStage string   `json:"moderation_stage"`
		} `json:"moderation_details"`
	}
	if err := json.Unmarshal([]byte(apiError.RawJSON()), &body); err != nil {
		panic(err)
	}

	hint := "This request could not be completed because it did not meet safety requirements."
	if slices.Contains(body.ModerationDetails.Categories, "harassment") {
		hint = "Try removing abusive or targeting language and focus on neutral visual details instead."
	} else if body.ModerationDetails.ModerationStage == "input" {
		hint = "Try revising the prompt or input images and submit the request again."
	} else if body.ModerationDetails.ModerationStage == "output" {
		hint = "The generated result was blocked by a safety check. Try changing the prompt and generating again."
	}

	fmt.Printf("Image generation blocked (%s): %s\n", apiError.Code, hint)
}
```
