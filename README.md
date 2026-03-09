# UDF Converter API

UYAP UDF dosyalarını PDF ve DOCX formatlarına dönüştüren Flask API servisi.

## Özellikler

- UDF → PDF dönüştürme
- UDF → DOCX dönüştürme
- Docker ile kolay deployment
- CORS desteği
- Render.com ücretsiz plan uyumlu

## Kullanım

### Endpoint: POST /convert

**Parametreler:**
- `file`: UDF dosyası (multipart/form-data)
- `format`: `pdf` veya `docx`

**Örnek cURL:**
```bash
curl -X POST -F "file=@dosya.udf" -F "format=pdf" \
  https://udf-converter-api.onrender.com/convert --output sonuc.pdf
```

**Örnek JavaScript:**
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('format', 'pdf');

const response = await fetch('https://udf-converter-api.onrender.com/convert', {
  method: 'POST',
  body: formData
});

const blob = await response.blob();
// blob'u indir
```

## Sağlık Kontrolü

```bash
curl https://udf-converter-api.onrender.com/health
```

## Deployment

Render.com'da otomatik deploy edilir:

1. Render Dashboard'a gidin
2. "New Web Service" seçin
3. Bu repository'yi bağlayın
4. Environment: Docker
5. Plan: Free

## Teknolojiler

- **Flask**: Web framework
- **UDF-Toolkit**: UDF dönüştürme (Said Sürücü)
- **python-docx**: Word belgesi oluşturma
- **PyMuPDF**: PDF oluşturma
- **Gunicorn**: Production server

## Lisans

Bu proje [imer.av.tr](https://imer.av.tr) için geliştirilmiştir.

UDF-Toolkit: [github.com/saidsurucu/UDF-Toolkit](https://github.com/saidsurucu/UDF-Toolkit)
