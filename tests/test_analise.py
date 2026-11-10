import contextlib
import io
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

import analise  # noqa: E402


class BaseCSVTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def criar_csv(self, conteudo, nome="dados.csv", encoding="utf-8"):
        caminho = os.path.join(self._tmp.name, nome)
        with open(caminho, "w", encoding=encoding, newline="") as f:
            f.write(conteudo)
        return caminho


class TestCalcularMedia(BaseCSVTest):
    def test_media_inteiros(self):
        caminho = self.criar_csv("nome,valor\na,10\nb,20\nc,30\n")
        self.assertEqual(analise.calcular_media(caminho, "valor"), 20.0)

    def test_media_floats(self):
        caminho = self.criar_csv("valor\n1.5\n2.5\n3.5\n")
        self.assertAlmostEqual(analise.calcular_media(caminho, "valor"), 2.5)

    def test_celulas_em_branco_ignoradas(self):
        caminho = self.criar_csv("nome,valor\na,10\nb,\nc,  \nd,20\n")
        self.assertEqual(analise.calcular_media(caminho, "valor"), 15.0)

    def test_linha_curta_ignorada(self):
        caminho = self.criar_csv("nome,valor\na,10\nb\nc,20\n")
        self.assertEqual(analise.calcular_media(caminho, "valor"), 15.0)

    def test_arquivo_inexistente(self):
        caminho = os.path.join(self._tmp.name, "nao_existe.csv")
        with self.assertRaises(FileNotFoundError):
            analise.calcular_media(caminho, "valor")

    def test_coluna_desconhecida(self):
        caminho = self.criar_csv("nome,valor\na,10\n")
        with self.assertRaises(ValueError) as ctx:
            analise.calcular_media(caminho, "preco")
        self.assertIn("preco", str(ctx.exception))

    def test_arquivo_vazio(self):
        caminho = self.criar_csv("")
        with self.assertRaises(ValueError):
            analise.calcular_media(caminho, "valor")

    def test_valor_nao_numerico(self):
        caminho = self.criar_csv("nome,valor\na,10\nb,abc\n")
        with self.assertRaises(ValueError) as ctx:
            analise.calcular_media(caminho, "valor")
        self.assertIn("abc", str(ctx.exception))
        self.assertIn("3", str(ctx.exception))

    def test_coluna_sem_valores_numericos(self):
        caminho = self.criar_csv("nome,valor\na,\nb, \n")
        with self.assertRaises(ValueError) as ctx:
            analise.calcular_media(caminho, "valor")
        self.assertIn("valor", str(ctx.exception))


class TestMain(BaseCSVTest):
    def executar(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            codigo = analise.main(argv)
        return codigo, out.getvalue(), err.getvalue()

    def test_sucesso_imprime_media(self):
        caminho = self.criar_csv("valor\n10\n\n20\n")
        codigo, out, err = self.executar([caminho, "valor"])
        self.assertEqual(codigo, 0)
        self.assertEqual(out.strip(), "15.0")
        self.assertEqual(err, "")

    def test_erro_arquivo_inexistente(self):
        caminho = os.path.join(self._tmp.name, "nao_existe.csv")
        codigo, out, err = self.executar([caminho, "valor"])
        self.assertEqual(codigo, 1)
        self.assertEqual(out, "")
        self.assertTrue(err.startswith("Erro:"))

    def test_erro_coluna_desconhecida(self):
        caminho = self.criar_csv("valor\n1\n")
        codigo, out, err = self.executar([caminho, "outra"])
        self.assertEqual(codigo, 1)
        self.assertIn("Erro:", err)

    def test_erro_valor_nao_numerico(self):
        caminho = self.criar_csv("valor\nx\n")
        codigo, _, err = self.executar([caminho, "valor"])
        self.assertEqual(codigo, 1)
        self.assertIn("Erro:", err)


CSV_FILTRO = (
    "nome,idade,salario,cidade\n"
    "a,30,1000,SP\n"
    "b, 30 ,2000,\n"
    "c,40,xx,RJ\n"
    "d,30.0,9999,RJ\n"
    "e,50,,X\n"
)


class TestInterpretarFiltro(unittest.TestCase):
    def test_simples(self):
        self.assertEqual(analise.interpretar_filtro("idade=30"), ("idade", "30"))

    def test_divide_no_primeiro_igual(self):
        self.assertEqual(analise.interpretar_filtro("obs=a=b"), ("obs", "a=b"))

    def test_remove_espacos(self):
        self.assertEqual(analise.interpretar_filtro(" x = y "), ("x", "y"))

    def test_valor_vazio(self):
        self.assertEqual(analise.interpretar_filtro("cidade="), ("cidade", ""))

    def test_sem_igual(self):
        with self.assertRaises(ValueError):
            analise.interpretar_filtro("idade30")

    def test_nome_coluna_vazio(self):
        with self.assertRaises(ValueError):
            analise.interpretar_filtro("=1")
        with self.assertRaises(ValueError):
            analise.interpretar_filtro("  =1")


class TestCalcularMediaComFiltro(BaseCSVTest):
    def setUp(self):
        super().setUp()
        self.caminho = self.criar_csv(CSV_FILTRO)

    def test_media_apenas_linhas_correspondentes(self):
        # " 30 " casa com "30"; "30.0" nao casa; "xx" da linha c e ignorado
        self.assertEqual(
            analise.calcular_media(self.caminho, "salario", ("idade", "30")), 1500.0
        )

    def test_comparacao_exata_e_sensivel_a_maiusculas(self):
        caminho = self.criar_csv("cidade,valor\nSP,10\nsp,100\nSP ,20\n")
        self.assertEqual(analise.calcular_media(caminho, "valor", ("cidade", "SP")), 15.0)
        self.assertEqual(analise.calcular_media(caminho, "valor", ("cidade", "sp")), 100.0)

    def test_30_nao_casa_com_30_ponto_0(self):
        self.assertEqual(
            analise.calcular_media(self.caminho, "salario", ("idade", "30.0")), 9999.0
        )

    def test_valor_vazio_casa_celulas_vazias(self):
        self.assertEqual(
            analise.calcular_media(self.caminho, "salario", ("cidade", "")), 2000.0
        )

    def test_filtro_none_igual_ao_anterior(self):
        caminho = self.criar_csv("nome,valor\na,10\nb,\nc,20\n")
        self.assertEqual(
            analise.calcular_media(caminho, "valor", None),
            analise.calcular_media(caminho, "valor"),
        )
        self.assertEqual(analise.calcular_media(caminho, "valor", None), 15.0)

    def test_filtro_none_valor_invalido_ainda_falha(self):
        with self.assertRaises(ValueError):
            analise.calcular_media(self.caminho, "salario", None)

    def test_coluna_filtro_inexistente(self):
        with self.assertRaises(ValueError) as ctx:
            analise.calcular_media(self.caminho, "salario", ("nada", "1"))
        self.assertIn("nada", str(ctx.exception))

    def test_nenhuma_linha_corresponde(self):
        with self.assertRaises(ValueError) as ctx:
            analise.calcular_media(self.caminho, "salario", ("idade", "99"))
        self.assertIn("idade=99", str(ctx.exception))

    def test_correspondentes_somente_vazios(self):
        with self.assertRaises(ValueError):
            analise.calcular_media(self.caminho, "salario", ("idade", "50"))

    def test_nao_numerico_em_linha_correspondente_falha(self):
        with self.assertRaises(ValueError) as ctx:
            analise.calcular_media(self.caminho, "salario", ("idade", "40"))
        self.assertIn("xx", str(ctx.exception))
        self.assertIn("4", str(ctx.exception))


class TestMainComFiltro(BaseCSVTest):
    executar = TestMain.executar

    def test_filtro_sucesso(self):
        caminho = self.criar_csv(CSV_FILTRO)
        codigo, out, err = self.executar(
            [caminho, "salario", "--filtrar-coluna", "idade=30"]
        )
        self.assertEqual(codigo, 0)
        self.assertEqual(out.strip(), "1500.0")
        self.assertEqual(err, "")

    def test_filtro_coluna_inexistente(self):
        caminho = self.criar_csv(CSV_FILTRO)
        codigo, out, err = self.executar(
            [caminho, "salario", "--filtrar-coluna", "nada=1"]
        )
        self.assertEqual(codigo, 1)
        self.assertEqual(out, "")
        self.assertIn("Erro:", err)

    def test_filtro_mal_formatado_sai_com_2(self):
        caminho = self.criar_csv(CSV_FILTRO)
        for texto in ("idade30", "=1"):
            with self.subTest(texto=texto):
                err = io.StringIO()
                with contextlib.redirect_stderr(err), self.assertRaises(SystemExit) as ctx:
                    analise.main([caminho, "salario", "--filtrar-coluna", texto])
                self.assertEqual(ctx.exception.code, 2)
                self.assertIn("--filtrar-coluna", err.getvalue())


class TestMensagemFiltroInvalido(BaseCSVTest):
    def test_mensagem_formato_coluna_valor(self):
        caminho = self.criar_csv(CSV_FILTRO)
        err = io.StringIO()
        with contextlib.redirect_stderr(err), self.assertRaises(SystemExit) as ctx:
            analise.main([caminho, "salario", "--filtrar-coluna", "idade30"])
        self.assertEqual(ctx.exception.code, 2)
        self.assertIn(
            "argument --filtrar-coluna: use o formato coluna=valor", err.getvalue()
        )


class TestArquivoComBOM(BaseCSVTest):
    def setUp(self):
        super().setUp()
        self.caminho = self.criar_csv(
            "idade,salario\n30,1000\n40,2000\n30,3000\n", encoding="utf-8-sig"
        )
        with open(self.caminho, "rb") as f:
            self.assertEqual(f.read(3), b"\xef\xbb\xbf")

    def test_media_primeira_coluna_sem_filtro(self):
        self.assertAlmostEqual(analise.calcular_media(self.caminho, "idade"), 100 / 3)

    def test_media_primeira_coluna_com_filtro_na_primeira_coluna(self):
        self.assertEqual(
            analise.calcular_media(self.caminho, "idade", ("idade", "30")), 30.0
        )

    def test_filtro_na_primeira_coluna_media_de_outra(self):
        self.assertEqual(
            analise.calcular_media(self.caminho, "salario", ("idade", "30")), 2000.0
        )


if __name__ == "__main__":
    unittest.main()
