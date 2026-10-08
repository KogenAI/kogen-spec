# Recovery walks run.json, git, and process liveness. There is no pure apply.
# The process answers so the harness can record the miss. It does not reimplement §3.10.
defmodule Adapter do
  def observe do
    %{
      "last" => "no_seam",
      "line" => "no_seam",
      "claim" => "",
      "runs" => %{}
    }
  end

  # preserved means a durable copy of the latest work/candidate, never just
  # an older snapshot. Real Git/filesystem publication and cleanup have no seam.
  def validate!(%{"op" => "apply", "event" => %{"tag" => "Put", "value" => v}}) do
    for key <- ["work", "preserved", "preserveOk"] do
      true = is_boolean(Map.fetch!(v, key))
    end
  end
  def validate!(%{"op" => "apply", "event" => %{"tag" => "PreservationResult", "value" => v}}) do
    true = is_binary(Map.fetch!(v, "id"))
    true = is_boolean(Map.fetch!(v, "ok"))
  end
  def validate!(_), do: :ok

  def loop do
    case IO.binread(:stdio, :line) do
      :eof -> :ok
      {:error, _} -> :ok
      line ->
        validate!(JSON.decode!(String.trim(line)))
        IO.binwrite(:stdio, [JSON.encode!(observe()), "\n"])
        loop()
    end
  end
end

Adapter.loop()
